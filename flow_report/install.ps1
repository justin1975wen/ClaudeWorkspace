# install.ps1 — 一次性環境安裝
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Flow 工時統計表下載器 — 環境安裝 ===" -ForegroundColor Cyan
Write-Host ""

# 找到真正的 Python（避開 Windows Store 佔位程式）
$pythonExe = $null
$candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe"
)
foreach ($c in $candidates) {
    if (Test-Path $c) { $pythonExe = $c; break }
}
# 備用：py launcher
if (-not $pythonExe) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { $pythonExe = $py.Source }
}
if (-not $pythonExe) {
    Write-Error "找不到 Python，請安裝 Python 3.8+：https://python.org"
    exit 1
}
$pyVersion = & $pythonExe --version 2>&1
Write-Host "Python: $pyVersion  ($pythonExe)" -ForegroundColor Green

# 建立虛擬環境
$venvDir = Join-Path $ScriptDir ".venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "建立虛擬環境..."
    & $pythonExe -m venv $venvDir
    Write-Host "  ✓ 虛擬環境建立完成" -ForegroundColor Green
} else {
    Write-Host "  ✓ 虛擬環境已存在，略過" -ForegroundColor Gray
}

# 安裝 Python 套件
Write-Host "安裝 Python 套件（playwright）..."
& "$venvDir\Scripts\pip.exe" install -r "$ScriptDir\requirements.txt" --quiet
Write-Host "  ✓ 套件安裝完成" -ForegroundColor Green

# 安裝 Playwright Chromium 瀏覽器
Write-Host "安裝 Playwright Chromium 瀏覽器（約 100MB，請稍待）..."
& "$venvDir\Scripts\playwright.exe" install chromium
Write-Host "  ✓ Chromium 安裝完成" -ForegroundColor Green

Write-Host ""
Write-Host "安裝完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步："
Write-Host "  1. 執行  .\setup_auth.ps1   進行首次微軟帳號登入（含 MFA）"
Write-Host "  2. 執行  .\create_task.ps1  建立 Windows 每日排程工作"
