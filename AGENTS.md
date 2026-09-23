# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

MCP server (stdio) exposing 18 typed macOS automation tools over `/usr/bin/osascript` and a few system binaries. Python 3.13+, `uv`, single runtime dependency (`mcp`). macOS only.

## Commands

- `uv sync` — install dependencies into `.venv`
- `uv run osascript-mcp` / `uv run python -m osascript_mcp` — runs the server on stdio (it waits for JSON-RPC; it is not interactive)
- `uv run pytest -m unit` — unit + hypothesis property tests (pure functions, no macOS side effects)
- `uv run pytest -m integration` — integration suite (spawns the real server)
- `DEBUG=1 uv run pytest -m integration` — also prints the server's stderr (per-call log lines, shutdown messages)
- `uv run ruff check .` / `uv run ruff format .` — lint / format

There is no way to run a single integration case in isolation from the CLI beyond pytest's own `-k`/node-id selection (`uv run pytest tests/test_integration.py::test_name`).

## Tests are integration tests

`tests/test_integration.py` spawns the real server (via `OSASCRIPT_MCP_CMD`, default `sys.executable -m osascript_mcp`) and talks MCP over stdin/stdout using `mcp.ClientSession` + `stdio_client`. Calls hit real `osascript`, the real clipboard, real windows, and `screencapture`. Consequences:

- Running the suite changes the local machine's clipboard and may press keys, open apps, and show notifications.
- Tests that depend on TCC grants or a running browser must tolerate their absence: they use `pytest.skip(...)` or accept a permission error / timeout as a valid outcome. CI (`.github/workflows/test.yml`, macos-latest, Python 3.13) has no TCC grants and no Safari running.
- `CALL_TIMEOUT_S` (40s, in `tests/conftest.py`) must stay above the server's 30s default script timeout.
- The suite asserts `tools/list` returns exactly 18 tools.
- On this dev machine, three screenshot-related cases fail for a pre-existing reason unrelated to the port: Screen Recording permission is denied for Terminal, and `screencapture`'s failure text doesn't match the tolerance substrings those tests check for. The same three cases fail identically against the old Node server for the same reason — grant Screen Recording to the terminal/app running the tests to get a fully green run.

## Architecture

- `src/osascript_mcp/executor.py` — the only place child processes are spawned. `_spawn_guarded` runs every child in its own process group (`start_new_session=True`) with a minimal env (`PATH`, `HOME`, `LANG` only), behind a shared `asyncio.Semaphore(5)`, with SIGTERM → 2s → SIGKILL (via `os.killpg`) on the whole group and a forced return if pipes never close. Scripts go in via stdin (`osascript -`), never temp files. Output is capped at 100 KB per stream, decoded so a UTF-8 sequence split at the cap is dropped rather than mangled. Also owns `safe_error` (redacts paths incl. HFS `Macintosh HD:Users:` form, tokens, keys) and `classify_error` (maps osascript stderr/error codes such as -1743, -25211, -1728, -600 to a `category`; includes Russian-locale strings).
- `src/osascript_mcp/server.py` — `TOOLS` (a `list[mcp_types.Tool]` returned by `tools/list`) and `HANDLERS` (a plain `dict[str, Callable]`, looked up by exact key). Handler helpers: `run_as` (AppleScript → `{ok, stdout | error}`), `run_shell` (absolute-path binaries via `execute_command`, no shell), `text_result` (truncates at 50K chars), `error_result`, `untrusted_result`. The MCP server object is wired via the `mcp` SDK's low-level `Server` with `on_list_tools`/`on_call_tool` constructor callbacks (this SDK version has no decorator-based `@server.call_tool()` API and does not validate `arguments` against `inputSchema` — every handler validates its own input).

### Invariants to preserve when adding or changing a tool

- Adding a tool means touching: the `TOOLS` entry, a `HANDLERS[...]` function, the permission group arrays used by `check_permissions` (`ALWAYS_AVAILABLE` / `NEEDS_ACCESSIBILITY` / `NEEDS_AUTOMATION` / `NEEDS_SCREEN_RECORDING`), the tool-count assertion in `tests/test_integration.py`, and the README tool table/counts.
- The `mcp` SDK does not validate arguments against `inputSchema`. Every handler validates types itself (e.g. `finite_int` for numbers so `inf`/fractions/bools never reach script text — JSON delivers integral values like `1` as either `int` or `float` depending on the client, so `finite_int` must accept both).
- Any string interpolated into AppleScript goes through `escape_as`. Numbers are validated before interpolation. Values interpolated into JXA use `json.dumps`.
- Subprocesses other than osascript use `run_shell` with an absolute binary path (`BIN_SCREENCAPTURE`, `BIN_OPEN`, `BIN_SHORTCUTS`) and `--` before user-supplied positional args.
- Text that originates outside the server (clipboard, tab titles/URLs, window titles, menu items) is returned through `untrusted_result`.
- Records built in AppleScript are joined with `|||` and each field passes through the AppleScript `sanitizeField` helper (`AS_HELPERS`); the Python side drops any line that does not split into the expected field count.
- Do not set `text item delimiters` inside a `tell` block (breaks Safari, error -10006); set it after `end tell`.
- `open_url` enforces the http/https/mailto allowlist and normalizes control characters like the WHATWG URL parser before scheme sniffing; `file_open` must keep refusing anything that looks like a URL, otherwise `open(1)` bypasses that allowlist.
- Permission failures should return the specific System Settings pane (`ACCESSIBILITY_MSG`, category checks on `r["error"]["category"]`).
- Comments in this codebase record why a guard exists, often tied to a specific audit finding or observed macOS behaviour. Do not remove them.

## Versions and packaging

The version lives only in `pyproject.toml` (`[project].version`); `server.py` reads it at runtime via `importlib.metadata.version("osascript-mcp")`, so there is a single source of truth — no multi-file version bump. Distribution is git-only: `uvx --from git+https://github.com/pythoninthegrass/osascript-mcp osascript-mcp`. There is no PyPI package, no npm package, and no MCPB bundle.

## Context7

Always use Context7 MCP when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.

### Libraries

- astral-sh/docs
- jdx/mise
- mrlesk/backlog.md
- websites/taskfile_dev

<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management.

**CRITICAL RESOURCE**: Read `backlog://workflow/overview` to understand when and how to use Backlog for this project.

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

### Key MCP Commands

| Command | Purpose |
|---------|---------|
| `task_create` | Create a new task (status defaults to "To Do") |
| `task_edit` | Edit metadata, check ACs, update notes, change status |
| `task_view` | View full task details |
| `task_search` | Find tasks by keyword |
| `task_list` | List tasks with optional filters |
| `task_complete` | **Moves task to `backlog/completed/`** — only use for cleanup, not for marking done |

### Task Lifecycle

1. **Create**: `task_create` — new task in `backlog/tasks/`
2. **Start**: `task_edit(status: "In Progress")` — mark as active
3. **Done**: `task_edit(status: "Done")` — mark finished, stays in `backlog/tasks/` (visible on kanban)
4. **Archive**: `task_complete` — moves to `backlog/completed/` (use only when explicitly cleaning up)

**IMPORTANT**: Use `task_edit(status: "Done")` to mark tasks as done. Do NOT use `task_complete` unless the user explicitly asks to archive/clean up — it removes the task from the kanban.

### Preventing ID Collisions

Backlog.md does NOT enforce ID uniqueness on the filesystem. If two task files declare the same `id:` in their frontmatter, `task_view`/`task_search` silently resolve to whichever has the newer `updated_date`, hiding the other from the kanban and MCP lookups. This is how TASK-341 ended up with two owners (iOS-sync vs. Plex umbrella) in commit `89ff249`.

**Before creating any task, ALWAYS:**

1. Run `task_list` (or `rg "^id: TASK-" backlog/tasks/ backlog/archive/tasks/ backlog/completed/`) to find the highest existing ID.
2. Let `task_create` auto-assign the next ID — **never set `id:` manually in frontmatter or filenames**.
3. For subtasks, pass `parentTaskId` to `task_create` so Backlog.md generates the hierarchical ID (e.g., `TASK-342.1`) for you.

**Detecting a collision:**

```bash
rg -N "^id: " backlog/tasks/ backlog/archive/tasks/ backlog/completed/ \
  | awk -F': ' '{print $NF}' | sort | uniq -d
```

**Resolving a collision:** the MCP has no rename/change-id operation. Renumbering requires: (1) `git mv` the file to a new filename with the new ID; (2) edit the frontmatter `id:` field; (3) edit `parent_task_id:` if the task is a subtask whose parent was also renumbered (this field is NOT settable via `task_edit`); (4) edit `dependencies:` arrays in other tasks that reference the old ID; (5) verify with `rg "^id: TASK-OLD$" backlog/tasks/` returning zero results.

### Cross-Branch Task Scanning (disabled)

`check_active_branches` and `remote_operations` are both **disabled** in `backlog/config.yml`. With worktrees, these features scan other branches and pull in tasks that were already completed/archived on `main` but still exist in `backlog/tasks/` on older branches — bloating the kanban with ghost tasks. Do not re-enable without accounting for worktree branch divergence.

### Multiline Field Gotcha

The `finalSummary`, `description`, `implementationNotes`, and `planSet` MCP parameters are single-line JSON strings. Literal `\n` sequences are NOT interpreted as newlines — they render as the two characters `\` `n` in the markdown file. To write multiline content:

- Use `task_edit` with the field for short single-paragraph content
- For multiline content, edit the task markdown file directly with the file editing tool (the file path is shown in `task_view` output)

### Backlog MCP Parameter Reference (Common Pitfalls)

**`task_edit` parameter names are different from `task_create`:**

| Operation | `task_create` param | `task_edit` param |
|-----------|-------------------|-------------------|
| Task ID | — (auto-assigned) | **`id`** (NOT `taskId`) |
| Title | `title` | `title` |
| Description | `description` | `description` |
| Acceptance Criteria | `acceptanceCriteria` | **`acceptanceCriteriaSet`** (replaces all), `acceptanceCriteriaAdd`, `acceptanceCriteriaRemove`, `acceptanceCriteriaCheck`, `acceptanceCriteriaUncheck` |
| Dependencies | `dependencies` | `dependencies` |
| Parent Task | `parentTaskId` | **not supported — edit `parent_task_id:` in the markdown frontmatter directly** |
| Status | `status` | `status` |
| Notes | — | `notesAppend`, `notesSet`, `notesClear` |
| Plan | — | `planAppend`, `planSet`, `planClear` |
| Final Summary | — | `finalSummary`, `finalSummaryAppend` |
| References | `references` | `references`, `addReferences`, `removeReferences` |
| Documentation | `documentation` | `documentation`, `addDocumentation`, `removeDocumentation` |

**Common error:** Using `taskId` instead of `id`, or `acceptanceCriteria` instead of `acceptanceCriteriaSet` in `task_edit` calls. Always use `id` and the `acceptanceCriteria*` variant names, and `task_edit` cannot re-parent — edit the file's `parent_task_id:` frontmatter directly when a parent ID changes.

The overview resource contains additional detail on decision frameworks, search-first workflow, and guides for task creation, execution, and completion.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->
