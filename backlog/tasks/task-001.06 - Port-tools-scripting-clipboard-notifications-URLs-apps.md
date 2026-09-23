---
id: TASK-001.06
title: 'Port tools: scripting, clipboard, notifications, URLs, apps'
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:48'
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
- [x] #1 All 9 tools pass their corresponding integration test cases
- [x] #2 open_url normalizes control chars like WHATWG URL before scheme check
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ported run_osascript, get_clipboard, set_clipboard, send_notification, open_url, open_app, get_frontmost_app, file_open, run_shortcut into src/osascript_mcp/server.py with their TOOLS schemas copied verbatim from index.js and registered in HANDLERS. open_url normalizes control characters (strips TAB/CR/LF anywhere, trims leading/trailing C0/space) before scheme sniffing, matching WHATWG URL parser behavior, then validates against the http/https/mailto allowlist. run_shortcut stages text input to a 0600 temp file (never passes it as a literal CLI arg) and always places `--` immediately before the shortcut name so a name starting with `-` can't be parsed as a flag. TDD: ran the existing (pre-written, Node-validated) integration suite filtered to these 9 tools against the Python server first — 13 failed with "Unknown tool" as expected — then implemented until all 35 relevant integration cases pass. ruff check/format clean; full unit suite (77) still green.
<!-- SECTION:FINAL_SUMMARY:END -->
