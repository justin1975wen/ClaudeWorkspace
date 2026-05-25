# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workspace Overview

`D:\ClaudeWorkspace` is a general-purpose working directory, not a single project. Individual projects or scripts are created here as needed. There is no build system, test runner, or package manager at the workspace root.

## Environment

- **OS**: Windows 11, primary shell is PowerShell 5.1
- **Bash**: Available via WSL (use `Bash` tool for POSIX scripts; use `PowerShell` tool for Windows-native operations)
- **Preferred tool**: Use `PowerShell` for file operations, git, and process management; use `Bash` for shell scripts that target WSL paths (`~/.claude/...`)

## Claude Code Configuration

### Global settings — `C:\Users\hikar\.claude\settings.json`
- Theme: dark
- Status line: runs `bash ~/.claude/statusline-command.sh`
- Hook on `UserPromptSubmit`: runs `bash ~/.claude/hooks/session-time.sh` (5s timeout)

### Project permissions — `.claude/settings.local.json`
Pre-allowed operations include: `PowerShell`, `Bash` (curl, git, claude CLI, WSL helpers), `WebFetch` for `raw.githubusercontent.com` and `cc.lifehacker.tw`, and `Read` for `C:\Users\hikar\**`.

## Path Notes

- Claude global config lives at `C:\Users\hikar\.claude\` (maps to `~/.claude` inside WSL/Bash)
- WSL home (`$HOME`) is separate from the Windows user profile
- When running bash scripts that reference `~/.claude`, they resolve to the WSL home, not `C:\Users\hikar\.claude` — verify the path when troubleshooting hook or statusline issues

---

## Projects

### `flow_report/` — Flow WPG Holdings 工時統計表自動下載

Downloads a work-hours Excel report from the internal Flow system using Playwright + urllib. Uses a **traditional Python venv** (not uv) managed by `install.ps1`.

**First-time setup:**
```powershell
cd flow_report
.\install.ps1       # creates .venv, installs packages, installs Playwright Chromium
.\setup_auth.ps1    # interactive Microsoft login (saves auth_state.json)
.\create_task.ps1   # registers Windows Task Scheduler daily job
```

**Run manually:**
```powershell
& "D:\ClaudeWorkspace\flow_report\.venv\Scripts\python.exe" download_report.py
# or with visible browser for debugging:
& "D:\ClaudeWorkspace\flow_report\.venv\Scripts\python.exe" download_report.py --headed
```

**Exit codes:** 0 = success, 2 = session expired (re-run `setup_auth.ps1`), 1 = other error.

**Key paths:**
- `auth_state.json` — Playwright browser session (refreshed on each successful run)
- `D:\ClaudeWorkspace\reports\` — output xlsx files (named `工時統計表_YYYYMMDD.xlsx`)
- `download.log` — per-run log
- `scheduler.log` — Task Scheduler run log
- `debug/` — screenshots taken at each step; `debug/error_response.html` on POST failure

**Architecture:** Playwright navigates to the report page → clicks the 工時統計表 tab → waits for the Statistics iframe → sets date range via Telerik RadDatePicker JS API → clicks 查詢 → then bypasses Playwright's download interception by re-POSTing the form with cookies via `urllib` directly, and converts the HTML-XLS response to real xlsx via pandas.

### `postal-helper/` — 台灣郵遞區號查詢 CLI

Single-file CLI that queries the `zip5.5432.tw` API. Uses **uv** (no venv needed).

```powershell
# Windows (double-click or run):
.\postal-helper\zipcode.bat

# Direct:
uv run postal-helper\zipcode.py
```

---

## Python 環境

- `flow_report/` uses a **traditional venv** at `flow_report/.venv/` (managed by `install.ps1`); do not use uv here.
- `postal-helper/` uses **uv** (`uv run`); no venv setup needed.
- For any new scripts in this workspace, prefer **uv**.

---

## 12-Rule Behavior Guidelines

These rules apply to every task in this project unless explicitly overridden.
Bias: caution over speed on non-trivial work. Use judgment on trivial tasks.

### Rule 1 — Think Before Coding
State assumptions explicitly. If uncertain, ask rather than guess.
Present multiple interpretations when ambiguity exists.
Push back when a simpler approach exists.
Stop when confused. Name what's unclear.

### Rule 2 — Simplicity First
Minimum code that solves the problem. Nothing speculative.
No features beyond what was asked. No abstractions for single-use code.
Test: would a senior engineer say this is overcomplicated? If yes, simplify.

### Rule 3 — Surgical Changes
Touch only what you must. Clean up only your own mess.
Don't "improve" adjacent code, comments, or formatting.
Don't refactor what isn't broken. Match existing style.

### Rule 4 — Goal-Driven Execution
Define success criteria. Loop until verified.
Don't follow steps. Define success and iterate.
Strong success criteria let you loop independently.

### Rule 5 — Use the model only for judgment calls
Use me for: classification, drafting, summarization, extraction.
Do NOT use me for: routing, retries, deterministic transforms.
If code can answer, code answers.

### Rule 6 — Token budgets are not advisory
Per-task: 4,000 tokens. Per-session: 30,000 tokens.
If approaching budget, summarize and start fresh.
Surface the breach. Do not silently overrun.

### Rule 7 — Surface conflicts, don't average them
If two patterns contradict, pick one (more recent / more tested).
Explain why. Flag the other for cleanup.
Don't blend conflicting patterns.

### Rule 8 — Read before you write
Before adding code, read exports, immediate callers, shared utilities.
"Looks orthogonal" is dangerous. If unsure why code is structured a way, ask.

### Rule 9 — Tests verify intent, not just behavior
Tests must encode WHY behavior matters, not just WHAT it does.
A test that can't fail when business logic changes is wrong.

### Rule 10 — Checkpoint after every significant step
Summarize what was done, what's verified, what's left.
Don't continue from a state you can't describe back.
If you lose track, stop and restate.

### Rule 11 — Match the codebase's conventions, even if you disagree
Conformance > taste inside the codebase.
If you genuinely think a convention is harmful, surface it. Don't fork silently.

### Rule 12 — Fail loud
"Completed" is wrong if anything was skipped silently.
"Tests pass" is wrong if any were skipped.
Default to surfacing uncertainty, not hiding it.
