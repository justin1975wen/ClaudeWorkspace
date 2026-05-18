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
