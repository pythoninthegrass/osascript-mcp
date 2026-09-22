---
id: TASK-001.02
title: Scaffold uv project from screencap conventions
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
labels:
  - python-port
dependencies:
  - TASK-001.01
references:
  - /Users/lance/git/screencap/pyproject.toml
  - /Users/lance/git/screencap/ruff.toml
  - /Users/lance/git/screencap/taskfile.yml
parent_task_id: TASK-001
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create pyproject.toml (mcp dep, dev dependency-group, pytest markers unit/integration, asyncio_mode=auto), uv.lock, ruff.toml, taskfile.yml + taskfiles/uv.yml, .tool-versions, .pre-commit-config.yaml, following ~/git/screencap conventions (minus sh, python-decouple, FastMCP, devbox).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 uv sync succeeds and creates .venv
- [ ] #2 ruff.toml, taskfile.yml, .tool-versions, .pre-commit-config.yaml present and modeled on screencap
<!-- AC:END -->
