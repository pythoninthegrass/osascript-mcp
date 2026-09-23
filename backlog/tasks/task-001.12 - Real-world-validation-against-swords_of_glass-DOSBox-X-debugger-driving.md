---
id: TASK-001.12
title: Real-world validation against swords_of_glass (DOSBox-X debugger driving)
status: Done
assignee: []
created_date: '2026-09-22 23:04'
updated_date: '2026-09-23 02:35'
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
- [x] #1 Each osascript.md technique is exercised at least once through osascript-mcp tools (not raw osascript) against a real DOSBox-X session in swords_of_glass
- [x] #2 Window targeting by substring, menu-by-position clicking, and the digit-keystroke workaround are confirmed to work identically through the Python server
- [x] #3 Full cleanup (kill PID, close Terminal windows, verify via ps/get name of every window) is performed after the test session, leaving no orphaned windows or processes
- [x] #4 Any technique with no clean tool mapping is filed as a new backlog task instead of being silently patched around
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated swords_of_glass's .mcp.json to add an `osascript` entry (uvx --from git+https://github.com/pythoninthegrass/osascript-mcp), sorted alphabetically among the existing servers.

Drove a real DOSBox-X debugger session (Swords of Glass, /Applications/dosbox-x.app, real Terminal.app TTY, -break-start) entirely through the ported osascript-mcp server via an ad-hoc MCP client script, mapping each docs/osascript.md technique:

- Launch via `run_osascript` (`do script`) confirmed working; `do script`'s own return value is a tab/window reference, not stdout, so the doc's own `& echo $!` PID-capture trick doesn't carry a shell $! value out — `do shell script "pgrep -x dosbox-x"` after a plain foreground launch is the clean equivalent and was confirmed reliable. (Backgrounding the launch with `&` to try to combine PID-capture with launch is actively wrong for this app: it left DOSBox-X in a stopped/T process state instead of running under the debugger — the debugger needs to be the true foreground job.)
- Window substring targeting (`first window whose name contains "dosbox-x"`) and tab resize confirmed working via `run_osascript`; `manage_windows` list also correctly surfaced the window.
- AXRaise + frontmost before each keystroke burst confirmed load-bearing the hard way: a first attempt that also tried `tell application "Terminal" to set frontmost to true` (wrong verb for Terminal, -10006) aborted the whole script before reaching the System Events AXRaise/frontmost lines, so focus was never established and two `press_key` digit presses landed nowhere (screenshots identical before/after). Fixed to `tell application "Terminal" to activate` + System Events `set frontmost to true` / `perform action "AXRaise"`, confirmed working.
- **Digit-corruption bug reproduced exactly through the wrapper**: `press_key({"key": "1"})` then `{"key": "6"}` against the live debugger console produced `qv` on the input line — byte-for-byte the same corruption the doc documents for raw osascript. Confirmed via code read (`KEY_CODES` has no digit entries, falls through to `keystroke`) and confirmed the fix direction works: raw `key code 18` / `key code 22` via `run_osascript` lands `1`/`6` correctly. Filed as TASK-001.14 (no clean tool mapping exists in `press_key` today).
- `app_menu` list confirmed working against both Terminal and DOSBox-X (real menu bars, including DOSBox-X's Debug menu). Reading `handle_app_menu`'s click implementation showed it only supports name-based menu item references, with no position-based selector — the doc's specific workaround for accelerator-annotated names (`first menu item of menu 1 of ...`) has no path through `app_menu`. Filed as TASK-001.15.
- Screenshot-before-Return verification loop confirmed working (window mode correctly resolved the Terminal window on this multi-display setup).
- Cleanup performed and verified after every phase: killed dosbox-x by PID (SIGTERM sufficed), closed the Terminal window, re-verified via `ps aux` and `get name of every window`/`get id of every window`. One incidental complication: the user manually quit Terminal.app mid-session (to apply the Accessibility grant), which left a zombie window record (0 tabs, invisible to System Events, `close` silently no-op'd) after relaunch — resolved by quitting Terminal again, which cleared it. PEOPLE.DAT/VAULT.DAT (mutable save state) were backed up before starting and confirmed byte-identical afterward — no game state was mutated since keystroke bursts stopped before Return.

Two follow-up tasks filed per AC #4: TASK-001.14 (press_key digit key_code gap) and TASK-001.15 (app_menu position-based click gap).
<!-- SECTION:FINAL_SUMMARY:END -->
