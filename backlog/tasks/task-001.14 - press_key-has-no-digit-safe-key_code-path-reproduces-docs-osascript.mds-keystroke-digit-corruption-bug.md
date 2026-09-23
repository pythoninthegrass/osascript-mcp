---
id: TASK-001.14
title: >-
  press_key has no digit-safe key_code path (reproduces docs/osascript.md's
  keystroke-digit-corruption bug)
status: Done
assignee: []
created_date: '2026-09-23 02:34'
updated_date: '2026-09-23 02:39'
labels:
  - python-port
dependencies:
  - TASK-001.12
references:
  - /Users/lance/git/swords_of_glass/docs/osascript.md
  - src/osascript_mcp/server.py
parent_task_id: TASK-001
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found while doing the live DOSBox-X validation in TASK-001.12: `press_key`'s `KEY_CODES` table (server.py, ~line 384) only has named keys (return, tab, arrows, f-keys, etc.) — no entries for digits 0-9. `handle_press_key` (~line 441) falls through to `elif len(key) == 1: action = f'keystroke "{key}"'` for any single character not in the table, so `press_key({"key": "1"})` sends `keystroke "1"`, not `key code 18`.

This reproduces docs/osascript.md's documented bug byte-for-byte: calling `press_key` with `"1"` then `"6"` against a live DOSBox-X debugger console (real session, swords_of_glass, 2026-09-23) produced `qv` on the input line — the exact corruption the doc warns about. Confirmed the fix works: raw `key code 18` / `key code 22` via System Events lands the correct digits (no corruption) when issued through `run_osascript` directly — there's just no way to reach that path through `press_key`'s public API today.

Anyone driving a keystroke-sensitive DOS/legacy-app console (DOSBox-X debugger, similar ncurses/BIOS-era consoles) through `press_key` will hit silent digit corruption with no warning, and has to fall back to raw `run_osascript` + System Events `key code` to work around it — exactly the raw-osascript escape hatch the ported tool was supposed to remove.

Fix: extend `KEY_CODES` with digit entries (`"0"`-`"9"` -> the doc's table: 1=18, 2=19, 3=20, 4=21, 5=23, 6=22, 7=26, 8=28, 9=25, 0=29) so `press_key` routes digits through `key code` instead of `keystroke`, matching how every other single-char-but-special key already works. Add a unit test asserting digit keys produce a `key code` action, not `keystroke`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `press_key({"key": "<digit>"})` for 0-9 emits `key code <n>` (the doc's table), not `keystroke "<digit>"`
- [x] #2 A unit test covers all 10 digits and asserts the AppleScript action string uses `key code`
- [x] #3 README/tool description mentions digits are handled via key code, if worth calling out
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added digit entries (0-9) to KEY_CODES in server.py per docs/osascript.md's table, so press_key routes digits through `key code` instead of falling through to `keystroke`. Added a parametrized unit test (TestPressKeyDigits) covering all 10 digits, asserting the AppleScript action uses key code and never keystroke. Updated the press_key tool description to document the digit key_code behavior.
<!-- SECTION:FINAL_SUMMARY:END -->
