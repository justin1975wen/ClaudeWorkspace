# setup_auth.ps1 — 首次登入設定（或 session 過期後重新登入）
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "$ScriptDir\.venv\Scripts\python.exe"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if (-not (Test-Path $python)) {
    Write-Error "找不到虛擬環境，請先執行 .\install.ps1"
    exit 1
}

& $python "$ScriptDir\setup_auth.py"
