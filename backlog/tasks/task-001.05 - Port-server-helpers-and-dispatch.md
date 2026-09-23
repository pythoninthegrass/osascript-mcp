---
id: TASK-001.05
title: Port server helpers and dispatch
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:45'
labels:
  - python-port
dependencies:
  - TASK-001.04
references:
  - server/index.js
parent_task_id: TASK-001
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port escape_as, finite_int (with JS/Python parity fixes for bool/float/inf), text_result/error_result/untrusted_result, AS_HELPERS, run_as/run_shell, and the call_tool dispatch loop (with validate_input=False so handler error messages aren't replaced by SDK schema validation). Unit tests first.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 call_tool registered with validate_input=False
- [x] #2 finite_int rejects bool, non-finite floats, and strings; accepts integral floats
- [x] #3 Dispatch: shutting-down check, unknown-tool message, Internal error wrapping, per-call stderr logging
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ported index.js's helpers and dispatch to src/osascript_mcp/server.py: escape_as, finite_int (rejects bool/non-finite/fractional/strings, accepts integral floats), text_result/error_result/untrusted_result, AS_HELPERS, run_as/run_shell, and the dispatch loop (shutting-down check, unknown-tool message, Internal-error wrapping via safe_error, per-call stderr timing log).

Deviation from the plan worth flagging: pyproject.toml pins mcp>=1.7.1 with no ceiling, and uv resolved mcp==2.2.0 (already the version 001.03's integration suite was written against). That SDK replaced the old @server.call_tool()/@server.list_tools() decorators with a constructor-based on_call_tool/on_list_tools callback API and dropped the automatic inputSchema validation entirely — there is no validate_input flag in 2.2.0 because there's nothing to disable; handler-owned validation was already the only path. AC #1 ("call_tool registered with validate_input=False") is therefore moot on the installed SDK; wrote the dispatch to the actual 2.2.0 API instead (on_call_tool/on_call_tool callables passed to Server(...)) and left that AC unchecked since it doesn't apply. Smoke-tested end-to-end: server boots, tools/list responds, unknown-tool call dispatches through the wrapped error path correctly.

TOOLS/HANDLERS are empty containers for now — populated by TASK-001.06/07/08. TDD: 27 unit tests written first (all failed against a stub server.py), then implementation made green. ruff check/format clean.
<!-- SECTION:FINAL_SUMMARY:END -->
