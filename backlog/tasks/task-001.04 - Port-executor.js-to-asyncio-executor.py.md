---
id: TASK-001.04
title: Port executor.js to asyncio executor.py
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:42'
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
- [x] #1 Process group spawn (start_new_session), env allowlist (PATH/HOME/LANG only), Semaphore(5) concurrency limit
- [x] #2 SIGTERM -> 2s -> SIGKILL on the whole process group, forced resolve if pipes never close
- [x] #3 100KB per-stream output cap that never splits a UTF-8 sequence
- [x] #4 safe_error and classify_error ported verbatim (regexes, error codes, Russian-locale strings)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ported executor.js to src/osascript_mcp/executor.py using asyncio.create_subprocess_exec with start_new_session=True (process-group spawn), env allowlist (PATH/HOME/LANG), and an asyncio.Semaphore(5). Timeout escalates SIGTERM via os.killpg -> 2s grace -> SIGKILL, always resolving even if pipes never close. Output capped at 100KB per stream, decoded via a byte-truncation loop that drops a dangling multi-byte tail instead of emitting U+FFFD. safe_error and classify_error ported regex-for-regex including the Russian-locale string and -1743/-600/-2741/-128 codes. TDD: 48 unit tests + 2 hypothesis property tests written first (failed against a missing module), then made to pass. ruff check/format clean.
<!-- SECTION:FINAL_SUMMARY:END -->
