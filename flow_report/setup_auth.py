"""
首次設定：執行此腳本完成微軟帳號登入（含 MFA），儲存登入狀態供後續自動化使用。
僅需執行一次；登入 session 過期後重新執行即可。

腳本會自動偵測登入完成（無需按 Enter），最多等待 5 分鐘。
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent
AUTH_STATE_FILE = SCRIPT_DIR / "auth_state.json"
REPORT_URL = (
    "https://flow.wpgholdings.com/eforms/administration/"
    "IT_New_MISNeed_Report/Main_start.aspx?eformid=1219&item=ALLI000001"
)
LOGIN_DOMAINS = ["login.microsoftonline.com", "login.live.com", "login.windows.net"]
MAX_WAIT_SECONDS = 300  # 5 分鐘


async def setup():
    print("=" * 55)
    print("  Flow 工時統計表 — 首次登入設定")
    print("=" * 55)
    print()
    print("即將開啟瀏覽器，請：")
    print("  1. 輸入公司微軟帳號密碼")
    print("  2. 完成 MFA（手機 / Authenticator）驗證")
    print("  3. 等待 Flow 系統頁面載入完成")
    print()
    print("  ★ 登入成功後腳本會自動偵測並儲存狀態，無需按 Enter。")
    print(f"  ★ 最多等待 {MAX_WAIT_SECONDS // 60} 分鐘。")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        page = await context.new_page()

        print("正在開啟 Flow 系統...")
        await page.goto(REPORT_URL)

        # 自動輪詢，等待離開微軟登入頁面
        print("等待登入完成中（請在瀏覽器完成操作）...")
        elapsed = 0
        poll_interval = 2  # 秒

        while elapsed < MAX_WAIT_SECONDS:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            current_url = page.url
            on_login_page = any(d in current_url for d in LOGIN_DOMAINS)

            if not on_login_page:
                # 等待頁面穩定
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except PlaywrightTimeout:
                    pass

                final_url = page.url
                if any(d in final_url for d in LOGIN_DOMAINS):
                    continue  # 被重導回登入頁，繼續等

                print(f"  ✓  偵測到已登入：{final_url[:70]}")
                break

            if elapsed % 30 == 0:
                print(f"  ... 仍在等待（已等待 {elapsed} 秒）")
        else:
            print("逾時：超過 5 分鐘未完成登入，請重新執行。")
            await browser.close()
            sys.exit(1)

        # 儲存登入狀態
        state = await context.storage_state()
        AUTH_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print(f"\n  ✓  登入狀態已儲存至: {AUTH_STATE_FILE}")

        # 給使用者 3 秒看到訊息後自動關閉
        await asyncio.sleep(3)
        await browser.close()

    print()
    print("設定完成！現在可執行 download_report.py 下載報表，")
    print("或等待排程自動執行。")


if __name__ == "__main__":
    asyncio.run(setup())
