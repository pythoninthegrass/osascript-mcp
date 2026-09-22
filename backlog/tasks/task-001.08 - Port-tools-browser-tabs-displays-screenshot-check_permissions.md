---
id: TASK-001.08
title: 'Port tools: browser tabs, displays, screenshot, check_permissions'
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
labels:
  - python-port
dependencies:
  - TASK-001.03
  - TASK-001.05
parent_task_id: TASK-001
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port get_browser_tabs, get_displays, screenshot, check_permissions. Full integration suite must be green against Python after this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 4 tools pass their corresponding integration test cases
- [ ] #2 Full pytest -m integration suite green against the Python server
- [ ] #3 tools/list diff between Node and Python is empty (names, descriptions, inputSchemas)
<!-- AC:END -->
