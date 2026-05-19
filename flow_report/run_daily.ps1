# run_daily.ps1 - Windows Task Scheduler entry point
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python    = "$ScriptDir\.venv\Scripts\python.exe"
$logFile   = "$ScriptDir\scheduler.log"

function Write-Log($msg) {
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    $line | Out-File -Append -Encoding utf8 $logFile
}

Write-Log "=== Task started ==="

try {
    & $python "$ScriptDir\download_report.py"
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Log "Download succeeded"
    } elseif ($exitCode -eq 2) {
        Write-Log "Session expired - need re-auth. Run setup_auth.ps1"
        Add-Type -AssemblyName System.Windows.Forms
        $msg = "Flow: Microsoft session expired.`nPlease run setup_auth.ps1 to re-authenticate."
        [System.Windows.Forms.MessageBox]::Show(
            $msg, "Flow Report", 0, 48
        ) | Out-Null
    } else {
        Write-Log "Download failed (exit: $exitCode)"
        Add-Type -AssemblyName System.Windows.Forms
        $msg = "Flow report download failed.`nCheck log: $ScriptDir\download.log"
        [System.Windows.Forms.MessageBox]::Show(
            $msg, "Flow Report Error", 0, 16
        ) | Out-Null
    }
} catch {
    Write-Log "Exception: $_"
}

Write-Log "=== Task finished (exit: $exitCode) ==="
