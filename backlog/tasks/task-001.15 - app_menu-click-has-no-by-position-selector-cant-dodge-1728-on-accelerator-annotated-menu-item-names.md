---
id: TASK-001.15
title: >-
  app_menu click has no by-position selector (can't dodge -1728 on
  accelerator-annotated menu item names)
status: To Do
assignee: []
created_date: '2026-09-23 02:34'
labels:
  - python-port
dependencies:
  - TASK-001.12
references:
  - /Users/lance/git/swords_of_glass/docs/osascript.md
  - src/osascript_mcp/server.py
parent_task_id: TASK-001
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found while doing the live DOSBox-X validation in TASK-001.12: docs/osascript.md documents a specific -1728 ("Can't get object") failure when clicking a menu item by its full accelerator-annotated name (e.g. `"Start DOSBox-X Debugger [Alt+F12]"`), and the workaround is to select by position instead: `first menu item of menu 1 of menu bar item "<Menu>" of menu bar 1`.

`handle_app_menu`'s "click" action (server.py ~line 686-693) only builds name-based references — it walks `menu_path` constructing `menu "X" of menu bar item "X" of menu bar 1` for every segment, with no way to say "first item" / "item at index N" instead of a literal name. So the exact technique the doc calls out (position-based selection to dodge the accelerator-name -1728) has no path through `app_menu` today; the only escape hatch is dropping to raw `run_osascript` + System Events, same as the digit-keystroke gap in TASK-001.14.

Fix options to consider: accept a numeric string/int in `menu_path` segments meaning "nth item" (e.g. `["Debug", 1]` -> `first menu item of menu 1 of menu bar item "Debug" of menu bar 1`), or add a separate `index` parameter for the final segment. Whatever the shape, `app_menu`'s existing "if not found, list what's there" error-recovery behavior should still work for the name-based path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 app_menu click supports selecting a menu item by ordinal position, not just by literal name
- [ ] #2 A test exercises position-based click against an app with an accelerator-annotated menu item name
- [ ] #3 Existing name-based click behavior and its "item not found, here's what's there" error path are unaffected
<!-- AC:END -->
