---
id: TASK-002
title: Add TOON output formatting option for tool results
status: To Do
assignee: []
created_date: '2026-09-22 23:29'
labels:
  - enhancement
dependencies: []
references:
  - 'https://github.com/toon-format/toon-python'
  - 'https://github.com/toon-format/toon'
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an opt-in TOON (Token-Oriented Object Notation) encoding for tool results returned by the MCP server, to reduce token usage for large/tabular outputs (e.g. window lists, tab lists, permission reports) consumed by LLM clients.

TOON is a compact, schema-aware JSON encoding (YAML-like indentation + CSV-like tabular arrays) that claims 30-60% fewer tokens than JSON for uniform array data. Reference implementation and spec:
- `toon-format/toon` — https://github.com/toon-format/toon — TypeScript SDK, CLI, benchmarks, and `SPEC.md`. This is the canonical implementation to depend on; check its `packages/` directory for the current published npm package name at implementation time, since the previous `@toon-format/toon` package is being retired/renamed and should not be assumed current.
- Python reference implementation for spec/behavior comparison only (this server is Node/ESM, not Python): `toon-format/toon-python` — https://github.com/toon-format/toon-python

Since this server is Node/ESM with a single runtime dependency (`@modelcontextprotocol/sdk`), the implementation dependency should come from `toon-format/toon`'s current TS/JS package; use toon-python only as a cross-reference for spec conformance if behavior is ambiguous.

Scope:
- Evaluate which existing handlers return array/tabular data that would benefit (e.g. list_windows, list_tabs, list_open_apps, check_permissions).
- Decide whether TOON encoding is a new output helper (parallel to `textResult`/`untrustedResult`) gated by a tool argument or server capability, not a silent behavior change.
- Preserve `untrustedResult` redaction/escaping semantics — TOON encoding must not bypass existing sanitization of untrusted text (clipboard, window titles, tab titles/URLs).
- Add/adjust tests in `server/test.js` and update the README tool table if `inputSchema` changes on any tool.

Out of scope: changing the default output format for existing tools without an explicit opt-in.
<!-- SECTION:DESCRIPTION:END -->
