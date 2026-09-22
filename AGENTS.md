# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

MCP server (stdio) exposing 18 typed macOS automation tools over `/usr/bin/osascript` and a few system binaries. Node >=18, ESM, single runtime dependency (`@modelcontextprotocol/sdk`). macOS only.

## Commands

- `npm install` / `npm ci`
- `npm start` — runs `server/index.js` on stdio (it waits for JSON-RPC; it is not interactive)
- `npm test` — runs `server/test.js`
- `DEBUG=1 npm test` — also prints the server's stderr (per-call log lines, shutdown messages)

There is no linter, formatter, or build step. There is no way to run a single test: `server/test.js` is one sequential script (`runTests()`) with a hand-rolled `assert`/`skip`. To iterate on one case, temporarily comment out the others or copy the relevant `send("tools/call", …)` lines into a scratch script.

## Tests are integration tests

`server/test.js` spawns the real server and talks JSON-RPC over stdin/stdout. Calls hit real `osascript`, the real clipboard, real windows, and `screencapture`. Consequences:

- Running the suite changes the local machine's clipboard and may press keys, open apps, and show notifications.
- Tests that depend on TCC grants or a running browser must tolerate their absence: they use `skip(name, why)` or accept a permission error / timeout as a valid outcome (see commits 767ced7, 5eb8fdf). CI (`.github/workflows/test.yml`, macos-latest, Node 18 and 22) has no TCC grants and no Safari running.
- `TEST_TIMEOUT_MS` (40s) must stay above the server's 30s default script timeout.
- The suite asserts `tools/list` returns exactly 18 tools.

## Architecture

- `server/executor.js` — the only place child processes are spawned. `spawnGuarded` runs every child in its own process group (`detached: true`) with a minimal env (`PATH`, `HOME`, `LANG` only), behind a shared semaphore (`MAX_CONCURRENT = 5`), with SIGTERM → 2s → SIGKILL on the whole group and a forced resolve if pipes never close. Scripts go in via stdin (`osascript -`), never temp files. Output is capped at 100 KB with `StringDecoder` so UTF-8 is never split. Also owns `safeError` (redacts paths incl. HFS `Macintosh HD:Users:` form, tokens, keys) and `classifyError` (maps osascript stderr/error codes such as -1743, -25211, -1728, -600 to a `category`; includes Russian-locale strings).
- `server/index.js` — `TOOLS` (schemas/descriptions returned by `tools/list`) and `HANDLERS` (an `Object.create(null)` map, dispatched with `Object.hasOwn`). Handler helpers: `runAS` (AppleScript → `{ok, stdout | error}`), `runShell` (absolute-path binaries via `executeCommand`, no shell), `textResult` (truncates at 50K chars), `errorResult`, `untrustedResult`.

### Invariants to preserve when adding or changing a tool

- Adding a tool means touching: the `TOOLS` entry, a `HANDLERS[...]` function, the permission group arrays used by `check_permissions` (`ALWAYS_AVAILABLE` / `NEEDS_ACCESSIBILITY` / `NEEDS_AUTOMATION` / `NEEDS_SCREEN_RECORDING`), the tool-count assertion in `server/test.js`, `manifest.json` (tools list), and the README tool table/counts.
- The MCP SDK does not validate arguments against `inputSchema`. Every handler validates types itself (e.g. `finiteInt` for numbers so `Infinity`/fractions never reach script text).
- Any string interpolated into AppleScript goes through `escapeAS`. Numbers are validated before interpolation. Values interpolated into JXA use `JSON.stringify`.
- Subprocesses other than osascript use `runShell` with an absolute binary path (`BIN_SCREENCAPTURE`, `BIN_OPEN`, `BIN_SHORTCUTS`) and `--` before user-supplied positional args.
- Text that originates outside the server (clipboard, tab titles/URLs, window titles, menu items) is returned through `untrustedResult`.
- Records built in AppleScript are joined with `|||` and each field passes through the AppleScript `sanitizeField` helper (`AS_HELPERS`); the JS side drops any line that does not split into the expected field count.
- Do not set `text item delimiters` inside a `tell` block (breaks Safari, error -10006); set it after `end tell`.
- `open_url` enforces the http/https/mailto allowlist; `file_open` must keep refusing anything that looks like a URL, otherwise `open(1)` bypasses that allowlist.
- Permission failures should return the specific System Settings pane (`ACCESSIBILITY_MSG`, category checks on `r.error.category`).
- Comments in this codebase record why a guard exists, often tied to a specific audit finding or observed macOS behaviour. Do not remove them.

## Versions and packaging

The version appears in `package.json`, `manifest.json` (MCPB bundle for Claude Desktop), `server.json` (MCP Registry), and the `new Server({ version })` call in `server/index.js`. These are currently out of sync (`server.json` is 1.1.3, the rest 1.2.0). Bump all of them together. `package.json` `files` controls the npm tarball; `.mcpbignore` controls the MCPB bundle (it excludes `server/test.js`).

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
