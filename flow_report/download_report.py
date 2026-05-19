"""
Flow WPG Holdings 工時統計表自動下載
用法: python download_report.py [--headed]
  --headed   以有頭模式執行（除錯用）
"""
import asyncio
import json
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent
AUTH_STATE_FILE = SCRIPT_DIR / "auth_state.json"
DOWNLOAD_DIR = Path(r"D:\ClaudeWorkspace\reports")
REPORT_URL = (
    "https://flow.wpgholdings.com/eforms/administration/"
    "IT_New_MISNeed_Report/Main_start.aspx?eformid=1219&item=ALLI000001"
)
START_DATE = datetime(2022, 1, 1)   # 固定起始日
LOG_FILE = SCRIPT_DIR / "download.log"
DEBUG_DIR = SCRIPT_DIR / "debug"

HEADED = "--headed" in sys.argv


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


async def screenshot(page_or_frame, name: str):
    DEBUG_DIR.mkdir(exist_ok=True)
    try:
        await page_or_frame.screenshot(path=DEBUG_DIR / f"{name}.png", full_page=True)
    except Exception:
        pass


async def wait_idle(target, timeout_ms=10000):
    try:
        await target.wait_for_load_state("networkidle", timeout=timeout_ms)
    except PlaywrightTimeout:
        pass


async def get_content_frame(page, timeout_s=15):
    """等待並回傳含有 Statistics 表單的 iframe"""
    for _ in range(timeout_s * 2):
        for frame in page.frames:
            if "Statist" in frame.url:
                return frame
        await asyncio.sleep(0.5)
    return None


async def set_date_telerik(frame, field_id: str, date: datetime):
    """
    設定 Telerik RadDatePicker 的日期。
    先透過 JS API 設定，再直接填 input 作為備援。
    """
    m, d, y = date.month, date.day, date.year
    date_str = f"{m}/{d}/{y}"   # M/D/YYYY 格式（符合頁面格式）

    # 方法 1：Telerik API（最可靠）
    set_ok = await frame.evaluate(f"""() => {{
        try {{
            var picker = $find('{field_id}');
            if (picker) {{
                picker.set_selectedDate(new Date({y}, {m - 1}, {d}));
                return true;
            }}
        }} catch(e) {{}}
        return false;
    }}""")

    # 方法 2：直接填入 _dateInput 欄位
    input_sel = f"#{field_id}_dateInput"
    try:
        inp = frame.locator(input_sel)
        await inp.triple_click(timeout=3000)
        await inp.fill(date_str, timeout=3000)
        await inp.press("Tab")
    except Exception:
        pass

    return set_ok


async def download_report():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now()
    today_file = today.strftime("%Y%m%d")

    if not AUTH_STATE_FILE.exists():
        log("錯誤：找不到登入狀態，請先執行 setup_auth.ps1 進行初始登入。")
        sys.exit(1)

    log(f"開始下載工時統計表（{START_DATE.strftime('%Y/%m/%d')} ~ {today.strftime('%Y/%m/%d')}）")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not HEADED,
            args=["--ignore-certificate-errors"],
        )
        context = await browser.new_context(
            storage_state=str(AUTH_STATE_FILE),
            accept_downloads=True,
            ignore_https_errors=True,
        )
        page = await context.new_page()

        try:
            # ── 1. 開啟主頁面 ─────────────────────────────────────────────
            log("連接 Flow 系統...")
            await page.goto(REPORT_URL, timeout=30000)
            await wait_idle(page, 20000)
            await screenshot(page, "01_loaded")

            if any(d in page.url for d in ["login.microsoftonline.com", "login.live.com"]):
                log("錯誤：登入狀態已過期，請重新執行 setup_auth.ps1。")
                (DOWNLOAD_DIR / "NEEDS_REAUTH.txt").write_text(
                    f"Flow 工時統計表登入已過期\n時間：{datetime.now().isoformat()}\n",
                    encoding="utf-8",
                )
                sys.exit(2)

            log("  ✓  頁面載入成功")

            # ── 2. 點擊「工時統計表」Tab ──────────────────────────────────
            log("點擊「工時統計表」tab...")
            await page.click("text=工時統計表", timeout=10000)
            await wait_idle(page, 10000)
            log("  ✓  Tab 已點擊")

            # ── 3. 取得內容 iframe ────────────────────────────────────────
            log("等待表單 iframe 載入...")
            frame = await get_content_frame(page, timeout_s=20)
            if frame is None:
                await screenshot(page, "03_no_frame")
                raise RuntimeError("找不到 Statistics 表單 iframe，請查看截圖 03_no_frame.png")
            await wait_idle(frame, 10000)
            log(f"  ✓  iframe 就緒：{frame.url[:70]}")
            await screenshot(page, "03_frame_ready")

            # ── 4. 設定日期範圍 ───────────────────────────────────────────
            log(f"設定日期：{START_DATE.strftime('%m/%d/%Y')} ~ {today.strftime('%m/%d/%Y')}")

            start_ok = await set_date_telerik(frame, "radApplyDateS", START_DATE)
            end_ok   = await set_date_telerik(frame, "radApplyDateE", today)

            log(f"  起始日期：{'✓' if start_ok else '手動填入'}")
            log(f"  結束日期：{'✓' if end_ok   else '手動填入'}")
            await screenshot(page, "04_dates_set")

            # ── 5. 點擊「查詢」取得資料 ───────────────────────────────────
            log("點擊「查詢」...")
            await frame.click("#btnSearch", timeout=10000)
            await wait_idle(frame, 30000)
            log("  ✓  查詢完成")
            await screenshot(page, "05_after_search")

            # ── 6. 用 urllib 直接 POST 取得 Excel ────────────────────────
            # headless iframe 觸發的表單下載 Playwright 無法捕捉，
            # 改以 Python urllib 帶 cookie 直接 POST，繞過 SSL 驗證。
            log("收集表單欄位並直接 POST 取得 Excel...")

            # 6a. 從 iframe 讀取所有表單欄位值
            form_pairs = await frame.evaluate("""() => {
                const form = document.querySelector('form');
                const pairs = [];
                for (const el of form.elements) {
                    if (!el.name) continue;
                    if (el.type === 'image') continue;
                    if ((el.type === 'checkbox' || el.type === 'radio') && !el.checked) continue;
                    pairs.push([el.name, el.value]);
                }
                pairs.push(['ibExcel.x', '16']);
                pairs.push(['ibExcel.y', '16']);
                return pairs;
            }""")
            log(f"  ✓  表單欄位 {len(form_pairs)} 個")

            # 6b. 從 context 取得 cookies
            auth_state = await context.storage_state()
            cookies_hdr = "; ".join(
                f"{c['name']}={c['value']}"
                for c in auth_state["cookies"]
                if "wpgholdings.com" in c.get("domain", "")
            )

            # 6c. 建立 SSL context（忽略公司自簽憑證）
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

            # 6d. 執行 POST（同步，在 executor 中執行以不阻塞事件迴圈）
            post_url  = frame.url
            post_body = urllib.parse.urlencode(
                [(str(k), str(v)) for k, v in form_pairs]
            ).encode("utf-8")
            headers = {
                "Content-Type":  "application/x-www-form-urlencoded",
                "Cookie":        cookies_hdr,
                "Referer":       post_url,
                "Origin":        "https://flow.wpgholdings.com",
                "User-Agent":    (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            }

            def do_post(attempt: int = 0):
                import time
                if attempt > 0:
                    wait = 30 * attempt
                    print(f"  重試第 {attempt} 次，等待 {wait} 秒後重試...")
                    time.sleep(wait)
                req = urllib.request.Request(
                    post_url, data=post_body, headers=headers, method="POST"
                )
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=180) as resp:
                    body = resp.read()
                    ct = resp.headers.get("Content-Type", "")
                    cd = resp.headers.get("Content-Disposition", "")
                return body, ct, cd

            log("  POST 中（伺服器產生報表，請稍候）...")
            loop = asyncio.get_event_loop()
            last_err = None
            for attempt in range(3):
                try:
                    body, ct, cd = await loop.run_in_executor(None, do_post, attempt)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    log(f"  ⚠  POST 失敗（{e}），{'重試中...' if attempt < 2 else '已達最大重試次數'}")
            if last_err:
                raise last_err
            log(f"  ✓  收到回應 {len(body)} bytes | ct={ct[:50]} | cd={cd[:60]}")

            # 6e. 判斷副檔名並儲存
            # 優先以 Content-Disposition filename 決定副檔名
            if "filename=" in cd:
                raw_name = cd.split("filename=")[-1].strip().strip('"').strip("'")
                ext = Path(raw_name).suffix or ".xls"
            elif "openxmlformats" in ct.lower():
                ext = ".xlsx"
            elif "excel" in ct.lower() or "spreadsheet" in ct.lower():
                ext = ".xls"
            elif body[:4] == b"PK\x03\x04":
                ext = ".xlsx"
            elif body[:4] == b"\xd0\xcf\x11\xe0":
                ext = ".xls"
            else:
                # 伺服器回傳非 Excel（含無附件 HTML）
                (DEBUG_DIR / "error_response.html").write_bytes(body)
                raise RuntimeError(
                    f"伺服器回傳非 Excel（{len(body)} bytes）\n"
                    f"Content-Type: {ct}\nContent-Disposition: {cd}\n"
                    f"已儲存至 debug/error_response.html 供檢查"
                )

            # 先存原始檔
            raw_path = DOWNLOAD_DIR / f"工時統計表_{today_file}{ext}"
            raw_path.write_bytes(body)
            log(f"  ✓  原始檔已儲存：{raw_path}")

            # 6f. HTML XLS → 真正的 xlsx（使用 pandas + openpyxl）
            save_path = DOWNLOAD_DIR / f"工時統計表_{today_file}.xlsx"
            log("  轉換為 .xlsx 格式中（資料量大，請稍候）...")

            def convert_to_xlsx(src: Path, dst: Path):
                dfs = pd.read_html(str(src), encoding="utf-8", header=0)
                with pd.ExcelWriter(str(dst), engine="openpyxl") as writer:
                    for i, df in enumerate(dfs):
                        sheet = f"Sheet{i+1}" if i > 0 else "工時統計表"
                        df.to_excel(writer, sheet_name=sheet, index=False)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, convert_to_xlsx, raw_path, save_path)

            # 刪除原始 HTML XLS
            raw_path.unlink(missing_ok=True)
            log(f"  ✓  報表已儲存：{save_path}")

            # 更新 auth state
            state = await context.storage_state()
            AUTH_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
            log("  ✓  已更新登入狀態")

            # 清除重新驗證旗標
            reauth_flag = DOWNLOAD_DIR / "NEEDS_REAUTH.txt"
            if reauth_flag.exists():
                reauth_flag.unlink()

        except SystemExit:
            raise
        except Exception as e:
            log(f"錯誤：{e}")
            await screenshot(page, "error")
            await browser.close()
            sys.exit(1)

        await browser.close()
        return save_path


if __name__ == "__main__":
    try:
        result = asyncio.run(download_report())
        log(f"=== 完成！{result} ===")
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        log(f"=== 失敗：{e} ===")
        sys.exit(1)
