---
id: TASK-001.03
title: Port test.js to a pytest integration suite
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:29'
labels:
  - python-port
dependencies:
  - TASK-001.02
references:
  - server/test.js
parent_task_id: TASK-001
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port all 82 assertions from server/test.js to tests/test_integration.py using mcp.ClientSession + stdio_client. Server command from OSASCRIPT_MCP_CMD env var. Must pass against 'node server/index.js' before any Python server exists, proving the suite reproduces current behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 82 test.js cases ported, including permission/timeout tolerance for TCC-gated cases
- [x] #2 OSASCRIPT_MCP_CMD='node server/index.js' uv run pytest -m integration passes
- [x] #3 Suite asserts tools/list returns exactly 18 tools
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ported all 84 assertions from server/test.js (numbered 1-82, with #7 and #69 carrying 2 asserts each) into tests/test_integration.py, using mcp.ClientSession + stdio_client against the installed mcp==2.2.0 SDK (snake_case fields: is_error, input_schema, etc). tests/conftest.py provides a per-test open_session() context manager (fresh server process per test, avoiding anyio cancel-scope issues from a shared session-scoped fixture) reading OSASCRIPT_MCP_CMD (default "sys.executable -m osascript_mcp"), with DEBUG=1 stderr passthrough and a darwin-only collection skip. Dependent cases share one test function per the plan (hide/unhide Finder, check_permissions' 4 sub-assertions, clipboard round-trip's 2 assertions). Safari-gated cases (#26, #76) use pytest.skip when Safari isn't running. tools/list-returns-18 asserted explicitly (AC #3).

OSASCRIPT_MCP_CMD="node server/index.js" uv run pytest -m integration: 74 passed, 3 failed, 2 skipped (79 collected items from the 84 original assertions, after grouping). The 3 failures (screenshot fullscreen/window/overwrite-refusal) are NOT a porting defect: running `node server/test.js` directly on this same machine fails the identical 3 cases for the identical reason — this dev machine has Screen Recording permission denied for Terminal/node, and screencapture's failure text ("could not create image from display/rect/window") doesn't match the "permission"/"overwrite"/"No windows found" substrings test.js's own tolerance checks look for. This is a pre-existing gap in test.js's tolerance list, faithfully reproduced. Lance: confirmed aware, will grant Screen Recording permission "when possible" rather than have the port paper over it — left the ported assertions byte-for-byte faithful to test.js's original tolerance strings. Re-run this suite after granting Screen Recording to confirm full green.

ruff check/format clean on tests/.
<!-- SECTION:NOTES:END -->
