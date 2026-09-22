---
id: TASK-001.03
title: Port test.js to a pytest integration suite
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
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
- [ ] #1 All 82 test.js cases ported, including permission/timeout tolerance for TCC-gated cases
- [ ] #2 OSASCRIPT_MCP_CMD='node server/index.js' uv run pytest -m integration passes
- [ ] #3 Suite asserts tools/list returns exactly 18 tools
<!-- AC:END -->
