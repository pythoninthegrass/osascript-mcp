---
id: TASK-001.02
title: Scaffold uv project from screencap conventions
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:15'
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
- [x] #1 uv sync succeeds and creates .venv
- [x] #2 ruff.toml, taskfile.yml, .tool-versions, .pre-commit-config.yaml present and modeled on screencap
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
pyproject.toml (name osascript-mcp, version 2.0.0, requires-python >=3.12, dep mcp>=1.7.1, dependency-groups.dev, pytest markers unit/integration, asyncio_mode=auto), ruff.toml, taskfile.yml + taskfiles/uv.yml, .pre-commit-config.yaml copied/adapted from ~/git/screencap (devbox/sh/python-decouple/fastmcp dropped per plan). Minimal src/osascript_mcp package (empty __init__, __main__ stub, server.main stub) added so uv sync can build the project. Per Lance mid-task: pinned to Python 3.13.6 (not 3.12) in .tool-versions and uv venv; uv sync succeeds, uv.lock generated.
<!-- SECTION:NOTES:END -->
