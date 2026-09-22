---
id: TASK-001.12
title: Real-world validation against swords_of_glass (DOSBox-X debugger driving)
status: To Do
assignee: []
created_date: '2026-09-22 23:04'
labels:
  - python-port
dependencies:
  - TASK-001.08
references:
  - /Users/lance/git/swords_of_glass/docs/osascript.md
parent_task_id: TASK-001
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the ported Python MCP server to drive ~/git/swords_of_glass's DOSBox-X debugger workflow, which today is done with raw 'osascript -e' calls (see docs/osascript.md). This exercises real, non-scripted usage beyond the integration suite and surfaces gaps the 82 ported test.js cases might miss.

Map each manual technique in docs/osascript.md to an osascript-mcp tool and confirm parity:
- 'osascript -e tell application Terminal to do script ...' launch -> run_osascript (applescript), capturing the launched PID the doc's cleanup section depends on.
- Resizing the Terminal tab, targeting 'first window whose name contains <substring>' (glyph-mismatch workaround for -1728) -> manage_windows / run_osascript; confirm substring-based window targeting still works through the wrapper.
- Menu access by position ('first menu item of menu 1 of menu bar item ...') to dodge -1728 on accelerator-annotated names -> app_menu list/click.
- Raising/focusing a window before each keystroke burst ('AXRaise' + 'set frontmost to true') -> manage_windows / app_visibility, called before each type_text/press_key burst.
- The digit-corruption bug (keystroke '16' arriving as 'qv') -> press_key with key_code-style single keys for digits vs type_text/keystroke for letters; confirm press_key's KEY_CODES table covers digits 0-9 and matches the doc's table.
- Screenshot-before-Return verification loop -> screenshot (window mode), confirming it resolves the right app/window and multi-display offset per the doc's notes.
- Cleanup: closing every spawned Terminal window by id, quitting the app by PID, verifying via 'ps aux' / 'get name of every window' -> run_osascript / app_visibility / manage_windows close.

Any technique that doesn't map cleanly onto an existing tool (e.g. capturing a launched PID from 'do script', or sheet/dialog detection) should be filed as a follow-up task rather than silently worked around.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each osascript.md technique is exercised at least once through osascript-mcp tools (not raw osascript) against a real DOSBox-X session in swords_of_glass
- [ ] #2 Window targeting by substring, menu-by-position clicking, and the digit-keystroke workaround are confirmed to work identically through the Python server
- [ ] #3 Full cleanup (kill PID, close Terminal windows, verify via ps/get name of every window) is performed after the test session, leaving no orphaned windows or processes
- [ ] #4 Any technique with no clean tool mapping is filed as a new backlog task instead of being silently patched around
<!-- AC:END -->
