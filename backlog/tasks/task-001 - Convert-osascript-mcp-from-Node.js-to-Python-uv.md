---
id: TASK-001
title: Convert osascript-mcp from Node.js to Python (uv)
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-23 04:41'
labels: []
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port the Node stdio MCP server (server/executor.js, server/index.js, server/test.js) to Python using uv and the official mcp SDK low-level Server, following ~/git/screencap conventions. Subprocesses via asyncio stdlib. Distribution is local/git only (uv run, uvx --from git+...). Node code is deleted once the Python suite is green. See plan: /Users/lance/.claude/plans/osascript-mcp-upstream-is-nodejs-sparkling-kitten.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 18 tools ported with identical names, descriptions, and inputSchemas
- [x] #2 Integration suite (ported from server/test.js) passes against the Python server
- [x] #3 Node implementation and packaging (server/, package*.json, manifest.json, server.json, .mcpbignore, glama.json) removed
- [x] #4 CI runs uv sync, ruff, and pytest on macos-latest
<!-- AC:END -->
