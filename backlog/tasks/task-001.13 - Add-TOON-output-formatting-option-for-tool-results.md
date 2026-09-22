---
id: TASK-001.13
title: Make TOON the default output format for tool results
status: To Do
assignee: []
created_date: '2026-09-22 23:34'
labels:
  - enhancement
dependencies:
  - TASK-001.12
references:
  - 'https://github.com/toon-format/toon-python'
  - 'https://github.com/toon-format/toon'
parent_task_id: TASK-001
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make TOON (Token-Oriented Object Notation) the default encoding for tool results returned by the (by-then Python) MCP server, to reduce token usage for large/tabular outputs (e.g. window lists, tab lists, permission reports) consumed by LLM clients.

This is the last subtask of the Node.js → Python conversion (TASK-001): it depends on TASK-001.12 (real-world validation) so it lands only once the server is fully Python, and it uses the Python TOON implementation rather than any JS one.

TOON is a compact, schema-aware JSON encoding (YAML-like indentation + CSV-like tabular arrays) claiming 30-60% fewer tokens than JSON for uniform array data. Reference/implementation:
- `toon-format/toon-python` — https://github.com/toon-format/toon-python — community-driven Python implementation of TOON; beta (v0.9.x), Python 3.8+, published to PyPI (`pip install git+https://github.com/toon-format/toon-python.git` until a stable PyPI release). Use this as the actual dependency added via `uv add`.
- `toon-format/toon` — https://github.com/toon-format/toon — canonical spec (`SPEC.md`) and TypeScript reference implementation; consult only for spec conformance questions, not as a runtime dependency (the JS implementation is not used post-conversion).

Scope:
- Evaluate which existing handlers return array/tabular data that would benefit (e.g. list_windows, list_tabs, list_open_apps, check_permissions).
- Replace the Python equivalents of `textResult`/`untrustedResult` with TOON-encoded output as the default for structured/tabular results — this is a default-behavior change, not a gated opt-in.
- Preserve `untrustedResult`-equivalent redaction/escaping semantics — TOON encoding must not bypass existing sanitization of untrusted text (clipboard, window titles, tab titles/URLs).
- Add/adjust pytest coverage and update the README tool table (including example outputs) to reflect TOON as the default response format.

Out of scope: keeping JSON as the default output format for any tool once this task lands.
<!-- SECTION:DESCRIPTION:END -->
