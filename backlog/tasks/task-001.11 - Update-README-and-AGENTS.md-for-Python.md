---
id: TASK-001.11
title: Update README and AGENTS.md for Python
status: Done
assignee: []
created_date: '2026-09-22 23:03'
updated_date: '2026-09-22 23:58'
labels:
  - python-port
dependencies:
  - TASK-001.09
parent_task_id: TASK-001
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update install instructions (uvx --from git+..., Claude Desktop mcpServers JSON), dev commands, test count, and AGENTS.md invariants/commands/versions section for the Python layout.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README shows uvx install and updated dev commands, no npm/.mcpb references
- [x] #2 AGENTS.md Commands/Architecture/invariants/versions sections match the Python layout
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.md: replaced the npm/.mcpb install flow with `uvx --from git+https://github.com/pythoninthegrass/osascript-mcp osascript-mcp` (Claude Desktop, Cursor/VS Code, Claude Code, and from-source dev configs), swapped the npm/Node/glama badges for macOS/Python/license/test-count/CI badges pointing at pythoninthegrass/osascript-mcp, replaced the "84 npm test" testing section with `uv run pytest -m unit` / `-m integration` (156 total: 77 unit + 79 integration) plus a note on the permission-tolerant integration cases, replaced the JS-specific "prototype pollution protection (Object.create(null))" comparison-table row with the Python-equivalent "unknown-tool dispatch guard" (plain dict keyed by exact name — no prototype chain to worry about), updated Requirements to Python 3.13+ / uv, and dropped the stale MCP-registry/glama-badge references (that identity/listing wasn't re-established for this repo). Zero remaining npm/.mcpb/Node references (verified by grep).

AGENTS.md: rewrote Commands (uv sync / uv run osascript-mcp / pytest -m unit|integration / ruff), Architecture (executor.py's asyncio primitives, server.py's TOOLS/HANDLERS dict and the on_list_tools/on_call_tool constructor-callback API — noting this mcp SDK version has no decorator-based call_tool and doesn't validate inputSchema, matching the deviation already flagged in TASK-001.05), the invariants list (escape_as/finite_int/run_shell/run_as/untrusted_result naming, finite_int's int-or-float acceptance), and Versions/packaging (single source of truth via importlib.metadata.version, git-only distribution, no PyPI/npm/MCPB). Left the two remaining "Node"/"npm" mentions in place deliberately — one documents the pre-existing Screen Recording permission gap also reproducing against the old Node server, the other explicitly states there is no npm package anymore.

markdownlint flagged some pre-existing inline-HTML and unlabeled-fence issues in README.md unrelated to this edit (present before this task, confirmed via git diff — not introduced here). ruff check/format clean, unit suite (77) green.
<!-- SECTION:FINAL_SUMMARY:END -->
