---
id: TASK-001.09
title: Remove Node implementation and packaging
status: To Do
assignee: []
created_date: '2026-09-22 23:03'
labels:
  - python-port
dependencies:
  - TASK-001.08
parent_task_id: TASK-001
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Delete server/, package.json, package-lock.json, manifest.json, .mcpbignore, server.json, glama.json. Update .gitignore to drop Node entries and add Python ones.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 server/*.js and npm/MCPB/registry files removed
- [ ] #2 .gitignore has .venv/, __pycache__/, .pytest_cache/, .ruff_cache/, .hypothesis/, dist/ and no leftover Node entries
<!-- AC:END -->
