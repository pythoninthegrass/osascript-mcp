---
id: TASK-001.06
title: 'Port tools: scripting, clipboard, notifications, URLs, apps'
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
labels:
  - python-port
dependencies:
  - TASK-001.03
  - TASK-001.05
parent_task_id: TASK-001
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port run_osascript, get_clipboard, set_clipboard, send_notification, open_url, open_app, get_frontmost_app, file_open, run_shortcut.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 9 tools pass their corresponding integration test cases
- [ ] #2 open_url normalizes control chars like WHATWG URL before scheme check
<!-- AC:END -->
