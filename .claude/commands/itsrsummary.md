---
name: itsrsummary
description: 自動下載 Flow WPG Holdings 工時統計表
---

執行 Flow WPG Holdings 工時統計表自動下載。

使用以下 PowerShell 指令執行下載腳本：

```powershell
& "D:\ClaudeWorkspace\flow_report\.venv\Scripts\python.exe" "D:\ClaudeWorkspace\flow_report\download_report.py" $ARGUMENTS
```

執行後依結果處理：
- **成功（exit 0）**：顯示儲存的檔案路徑與檔名
- **登入過期（exit 2）**：告知使用者需要重新驗證，請執行 `D:\ClaudeWorkspace\flow_report\setup_auth.ps1`
- **其他錯誤**：顯示錯誤訊息，並提示查看 `D:\ClaudeWorkspace\flow_report\download.log`
