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
