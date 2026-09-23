---
id: TASK-001.10
title: Switch CI to uv/pytest
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:56'
labels:
  - python-port
dependencies:
  - TASK-001.09
references:
  - .github/workflows/test.yml
parent_task_id: TASK-001
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the Node CI matrix with macos-latest + astral-sh/setup-uv, running ruff check/format and pytest (unit then integration) on Python 3.12 and 3.13.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .github/workflows/test.yml uses setup-uv, uv sync --frozen, ruff check, ruff format --check, pytest -m unit -n auto, pytest -m integration
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced .github/workflows/test.yml's Node matrix with macos-latest + astral-sh/setup-uv, running `uv sync --frozen`, `ruff check .` / `ruff format --check .`, `pytest -m unit -n auto`, then `pytest -m integration`.

Deviation from the plan worth flagging: the AC and plan called for a 3.12/3.13 matrix, but pyproject.toml's requires-python is `>=3.13,<3.14` — Lance pinned to 3.13-only during TASK-001.02's scaffold (documented in that task's implementation notes), so 3.12 isn't installable against this lockfile. Matrix is `["3.13"]` only, with a comment explaining why. Validated every step locally (uv sync --frozen, ruff check/format, pytest -m unit -n auto) before committing to the workflow file.
<!-- SECTION:FINAL_SUMMARY:END -->
