---
id: TASK-001.07
title: 'Port tools: accessibility and UI'
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:51'
labels:
  - python-port
dependencies:
  - TASK-001.03
  - TASK-001.05
parent_task_id: TASK-001
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port type_text, press_key, manage_windows, app_menu, app_visibility.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 5 tools pass their corresponding integration test cases
- [x] #2 manage_windows list emits null (not 0) for non-finite geometry
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ported type_text, press_key, manage_windows, app_menu, app_visibility into server.py with schemas copied verbatim. manage_windows list emits null for non-finite/non-parseable geometry (parse_num returns None instead of 0), matching the JS "never silently 0" invariant. Window index validation uses finite_int (rejects bools, fractional floats, non-finite) instead of a bare Python isinstance(int) check, since JSON delivers integral values like 1.0 as floats and JS's Number.isInteger would accept those. TDD: ran the pre-written integration suite filtered to these 5 tools against Python first (9 failed with "Unknown tool"), implemented until all 29 relevant cases pass. Full non-001.08 integration subset (65 tests) also green; only the 18-tools-list count test fails as expected since get_browser_tabs/get_displays/screenshot/check_permissions aren't wired yet. ruff check/format clean; unit suite (77) still green.
<!-- SECTION:FINAL_SUMMARY:END -->
