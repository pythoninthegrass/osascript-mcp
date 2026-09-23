---
id: TASK-001.13
title: Measure TOON vs JSON for tool results; default to minified JSON
status: Done
assignee: []
created_date: '2026-09-22 23:34'
updated_date: '2026-09-23 03:18'
labels:
  - enhancement
dependencies:
  - TASK-001.12
references:
  - 'https://github.com/toon-format/toon-python'
  - 'https://github.com/toon-format/toon'
modified_files:
  - pyproject.toml
  - src/osascript_mcp/server.py
  - tests/test_server.py
  - tests/test_integration.py
  - tests/conftest.py
  - bench/replay.py
  - README.md
parent_task_id: TASK-001
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Originally scoped to make TOON (Token-Oriented Object Notation) the default encoding for tool results, on the claim that TOON cuts 30-60% of tokens for tabular data. That claim was measured rather than assumed — see Implementation Notes for the real numbers — and the default landed on minified JSON instead, with TOON kept as an opt-in.

This is the last subtask of the Node.js → Python conversion (TASK-001): it depends on TASK-001.12 (real-world validation) so it lands only once the server is fully Python, and it uses the Python TOON implementation (`toon-format` on PyPI, pinned to `0.9.0b1` — the unpinned `0.1.0` release is a non-functional stub whose `encode()` raises `NotImplementedError`) rather than any JS one.

Scope (as executed):
- Added a single `encode_payload()` chokepoint in `server.py` dispatching on `OSASCRIPT_MCP_FORMAT` (`json-min` default, `json`, `toon`), replacing the ~9 scattered `json.dumps(..., indent=2)` output sites.
- Added `OSASCRIPT_MCP_CAPTURE=<path>` to append every structured payload as JSONL for offline replay (`bench/replay.py`), so the format comparison runs against real captured payloads, not synthetic ones.
- Flattened `manage_windows` list output's `position`/`size` nested objects into flat `x`/`y`/`width`/`height` columns — required for TOON's tabular form to win at all on that shape, and a strict improvement for minified JSON too. This is a breaking response-shape change, documented in the README.
- `untrusted_result`'s wrapper/redaction is unchanged; encoding happens inside it.
- Added unit coverage (format dispatch, TOON round-trip incl. a hypothesis property test on adversarial titles, capture-file writing) and updated the README (tool table, new "Output Format" section with verified example outputs, test counts).

Deviation from original scope: **"Out of scope: keeping JSON as the default output format for any tool" did not hold up against measurement.** `OSASCRIPT_MCP_FORMAT` is a permanent env var, not a temporary one, defaulting to `json-min`. See Implementation Notes for why.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Real captured payloads (not synthetic) from a live GUI-automation session are measured across json-indent2 / json-minified / toon before any default is chosen
- [x] #2 toon-format is pinned to an exact working version (0.9.0b1), not a floating range, because the unpinned PyPI 0.1.0 release is a non-functional stub
- [x] #3 encode_payload() is the single chokepoint for all structured tool output; error-message JSON and JXA-literal-escaping JSON are left untouched
- [x] #4 untrusted_result's redaction/escaping wrapper is preserved regardless of chosen encoding
- [x] #5 OSASCRIPT_MCP_FORMAT (json-min default / json / toon) and OSASCRIPT_MCP_CAPTURE are both covered by unit and integration tests
- [x] #6 README documents the output format, the manage_windows breaking shape change, and the measured decision with real numbers
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Measured with tiktoken (o200k_base) against a real capture (13 tool calls, 5 tools: manage_windows, app_menu, check_permissions, get_displays, get_frontmost_app) from a live GUI-automation session against actually-running apps (Finder, iTerm2, Typora, Firefox, Mail) — DOSBox-X was not running on this machine so the intended swords_of_glass TASK-017 session was substituted with the same tool repertoire against whatever was actually on screen.

Result: json-indent2=1236 tokens, json-min=764, toon=666. TOON beats today's indent2 baseline by 46% (mostly free — just dropping indentation) but only beats minified JSON by 12.8% overall, and regresses on small flat arrays like app_menu's menu-item lists (-5% vs minified — TOON's "[N]: " header doesn't amortize over 7-10 short strings). manage_windows (genuinely tabular, multiple windows) is TOON's best case at +17% vs minified.

Decision rule set before measuring: adopt TOON as default only if it beat minified JSON by >=15% on the real capture. 12.8% < 15%, so default is json-min, not toon. This directly overturned the task's original "out of scope: keeping JSON as default" line — recorded as a deviation in the description rather than silently ignored.

Caveat: the capture sample is thin (13 calls) and not the actual TASK-017 DOSBox-X debugger workload, which would likely have larger/more numerous window and tab lists and could tip the total over 15%. bench/replay.py is kept specifically so this can be re-measured against a real swords_of_glass session without re-deriving the harness.

toon-format packaging trap: `uv add toon-format` alone resolves to 0.1.0 (PyPI), whose encode() raises NotImplementedError. Must pin ==0.9.0b1.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built the measurement harness the original task lacked (encode_payload chokepoint, OSASCRIPT_MCP_CAPTURE, bench/replay.py) and used it on a real captured session instead of adopting TOON on faith. Real numbers: TOON beats today's pretty-printed JSON by 46% but only beats minified JSON by 12.8% overall, with an outright regression on small flat arrays (app_menu). Per a decision rule set before measuring, default became minified JSON (free, zero new dependency risk in the hot path); TOON remains available via OSASCRIPT_MCP_FORMAT=toon for tabular-heavy consumers. Flattened manage_windows position/size into columns along the way (breaking change, documented). 173 -> 176 tests, all green in all three formats; README and backlog task updated to reflect the measured outcome rather than the original assumption.
<!-- SECTION:FINAL_SUMMARY:END -->
