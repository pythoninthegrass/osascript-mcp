---
id: TASK-001.05
title: Port server helpers and dispatch
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
labels:
  - python-port
dependencies:
  - TASK-001.04
references:
  - server/index.js
parent_task_id: TASK-001
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port escape_as, finite_int (with JS/Python parity fixes for bool/float/inf), text_result/error_result/untrusted_result, AS_HELPERS, run_as/run_shell, and the call_tool dispatch loop (with validate_input=False so handler error messages aren't replaced by SDK schema validation). Unit tests first.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 call_tool registered with validate_input=False
- [ ] #2 finite_int rejects bool, non-finite floats, and strings; accepts integral floats
- [ ] #3 Dispatch: shutting-down check, unknown-tool message, Internal error wrapping, per-call stderr logging
<!-- AC:END -->
