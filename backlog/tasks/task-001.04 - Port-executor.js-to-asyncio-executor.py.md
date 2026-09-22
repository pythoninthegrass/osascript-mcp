---
id: TASK-001.04
title: Port executor.js to asyncio executor.py
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
labels:
  - python-port
dependencies:
  - TASK-001.02
references:
  - server/executor.js
parent_task_id: TASK-001
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port spawnGuarded, executeScript/executeCommand, safeError, classifyError to src/osascript_mcp/executor.py using asyncio stdlib. Write unit + hypothesis tests first (TDD).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Process group spawn (start_new_session), env allowlist (PATH/HOME/LANG only), Semaphore(5) concurrency limit
- [ ] #2 SIGTERM -> 2s -> SIGKILL on the whole process group, forced resolve if pipes never close
- [ ] #3 100KB per-stream output cap that never splits a UTF-8 sequence
- [ ] #4 safe_error and classify_error ported verbatim (regexes, error codes, Russian-locale strings)
<!-- AC:END -->
