---
id: TASK-001.10
title: Switch CI to uv/pytest
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
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
- [ ] #1 .github/workflows/test.yml uses setup-uv, uv sync --frozen, ruff check, ruff format --check, pytest -m unit -n auto, pytest -m integration
<!-- AC:END -->
