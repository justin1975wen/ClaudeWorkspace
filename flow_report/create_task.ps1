# create_task.ps1 — 建立 Windows 每日排程工作
# 用法：.\create_task.ps1 [-Time "09:00"]
param(
    [string]$Time = "08:30"
)

$TaskName  = "Flow工時統計表每日下載"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunScript = Join-Path $ScriptDir "run_daily.ps1"

Write-Host "建立排程工作：$TaskName" -ForegroundColor Cyan
Write-Host "  執行時間：每天 $Time"
Write-Host "  腳本路徑：$RunScript"
Write-Host ""

# 定義排程動作
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$RunScript`"" `
    -WorkingDirectory $ScriptDir

# 每日觸發（並在電腦開機後錯過的執行補跑）
$trigger = New-ScheduledTaskTrigger -Daily -At $Time

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew `
    -WakeToRun $false

$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited

# 若已存在則先移除
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "  已移除舊排程工作" -ForegroundColor Yellow
}

Register-ScheduledTask `
    -TaskName    $TaskName `
    -Action      $action `
    -Trigger     $trigger `
    -Settings    $settings `
    -Principal   $principal `
    -Description "每日下載 Flow WPG 工時統計表至 D:\ClaudeWorkspace\reports" | Out-Null

Write-Host "  ✓  排程工作建立成功！" -ForegroundColor Green
Write-Host ""
Write-Host "管理指令："
Write-Host "  立即測試：  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  查看狀態：  Get-ScheduledTask  -TaskName '$TaskName'"
Write-Host "  停用排程：  Disable-ScheduledTask -TaskName '$TaskName'"
Write-Host "  刪除排程：  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
Write-Host ""
Write-Host "下載目錄：D:\ClaudeWorkspace\reports"
