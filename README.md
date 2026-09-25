**Let Claude control your Mac.** Move windows, click menus, type text, read clipboard, manage browser tabs, take screenshots, run Shortcuts — 18 typed tools with input validation and security guardrails.

## Quick Start

Requires [uv](https://docs.astral.sh/uv/). Add this to your Claude Desktop config (`Settings → Developer → Edit Config`):

```json
{
  "mcpServers": {
    "osascript": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/pythoninthegrass/osascript-mcp", "osascript-mcp"]
    }
  }
}
```

Restart Claude, and you're ready.

<details>
<summary>Config for other clients (Cursor, VS Code, Claude Code)</summary>

**Cursor / VS Code (Copilot)**
```json
{
  "mcpServers": {
    "osascript": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/pythoninthegrass/osascript-mcp", "osascript-mcp"]
    }
  }
}
```

**Claude Code**
```bash
claude mcp add osascript -- uvx --from git+https://github.com/pythoninthegrass/osascript-mcp osascript-mcp
```

**From source (development)**
```bash
git clone https://github.com/pythoninthegrass/osascript-mcp.git
cd osascript-mcp && uv sync
# then use: "command": "uv", "args": ["run", "--directory", "/path/to/osascript-mcp", "osascript-mcp"]
```
</details>

## Try These Prompts

Once installed, ask Claude:

| Prompt | What happens |
|--------|-------------|
| *"Open Safari and show me what tabs I have"* | Launches Safari, reads all tab titles and URLs |
| *"Move the Finder window to the left half of my screen"* | Resizes and positions the window |
| *"Click File → Export as PDF in Keynote"* | Navigates the menu bar and clicks the item |
| *"Copy the URL from my active Chrome tab"* | Reads browser tabs, finds the active one |
| *"Type 'Hello World' into the active text field"* | Simulates keyboard input |
| *"Show a notification when you're done"* | Displays a native macOS banner |
| *"What app am I using right now?"* | Returns the frontmost app name and bundle ID |
| *"Press Cmd+Shift+4"* | Triggers the screenshot shortcut |
| *"List all items in the Edit menu of VS Code"* | Introspects the menu bar |
| *"Close the second window of Terminal"* | Targets a specific window by index |
| *"Screenshot the Safari window and save it to my Desktop"* | Captures just that window, not the whole screen |
| *"Which monitor is my Slack window on?"* | Reads display geometry and window positions |
| *"Hide everything except my editor"* | Hides apps without quitting them |
| *"Run my 'Daily Standup' shortcut"* | Invokes an Apple Shortcut by name |

## Tools

18 typed tools, each with input validation, error classification, and permission-aware error messages.

| Tool | What it does | Permission |
|------|-------------|------------|
| `check_permissions` | Report which permissions are granted and what each unlocks | None |
| `run_osascript` | Execute any AppleScript or JXA script | None |
| `get_clipboard` | Read clipboard as text | None |
| `set_clipboard` | Write text to clipboard | None |
| `send_notification` | Show macOS notification banner | None |
| `open_url` | Open URL in browser (http/https/mailto only) | None |
| `open_app` | Launch or bring app to front | None |
| `get_frontmost_app` | Get active app name + bundle ID | Automation |
| `get_browser_tabs` | List tabs in Safari, Chrome, or Arc | Automation |
| `type_text` | Type text into active app (max 500 chars) | Accessibility |
| `press_key` | Press key with modifiers (cmd+c, return, f5) | Accessibility |
| `manage_windows` | List (flat `x`/`y`/`width`/`height` fields) / move / resize / minimize / fullscreen / close | Accessibility |
| `get_displays` | List monitors — position, size, which is main | None |
| `app_menu` | List or click menu items in any app | Accessibility |
| `screenshot` | Capture full screen, a region, or an app window | Screen Recording |
| `app_visibility` | Hide, unhide, or quit an application | Accessibility |
| `file_open` | Open a file or folder, optionally in a given app | None |
| `run_shortcut` | List or run Apple Shortcuts | None |

## Output Format

Structured results (window lists, browser tabs, menu items, `check_permissions`, ...) are
minified JSON by default — no dependency risk, no whitespace tax:

```
{"app":"Finder","windows":[{"index":1,"title":"Downloads","x":0,"y":0,"width":900,"height":600}]}
```

Set `OSASCRIPT_MCP_FORMAT=toon` to switch to [TOON](https://github.com/toon-format/toon)
(compact, tabular) encoding instead:

```
app: Finder
windows[1]{index,title,x,y,width,height}:
  1,Downloads,0,0,900,600
```

TOON was evaluated as the default (TASK-001.13): measured against real captured payloads
from this server it beat minified JSON by only ~13% overall, and was an outright regression
on small flat arrays like `app_menu`'s menu-item lists — not enough margin to justify a new
dependency as the default. It stays available for clients that want it and for payloads that
are large and uniformly tabular (long window/tab lists). `OSASCRIPT_MCP_FORMAT=json` restores
pretty-printed JSON for debugging. `bench/replay.py` reproduces the measurement against any
captured session (see `OSASCRIPT_MCP_CAPTURE` below).

## Self-Correcting Menus

When Claude tries to click a menu item that doesn't exist, the server automatically returns the list of available items at that level — so Claude can retry with the correct name. No other MCP server does this.

```
User:   "Click File → Export as PDF in Preview"
Claude: calls app_menu click ["File", "Export as PDF"]
Server: "Menu item 'Export as PDF' not found in 'File'.
         Available: ['New from Clipboard', 'Open...', 'Close', 'Save',
         'Duplicate', 'Rename...', 'Export...', 'Export as PDF...']"
Claude: calls app_menu click ["File", "Export as PDF..."]
Server: "Clicked: File > Export as PDF..."
```

## Why mcp-osascript?

| | mcp-osascript | steipete (880★) | peakmojo (464★) |
|---|:---:|:---:|:---:|
| Typed tools with validation | **18** | 2 (generic) | 1 (generic) |
| URL scheme allowlist | **http/https/mailto** | No | No |
| Env isolation (child process) | **PATH+HOME+LANG only** | Full process env | Full process env |
| Process group kill (no orphans) | **SIGTERM→SIGKILL** | No | No |
| Error sanitization (paths, tokens) | **Yes** | No | No |
| Unknown-tool dispatch guard | **Yes** | No | No |
| Self-correcting menu click | **Yes** | No | No |
| Test suite | **176 (unit + integration)** | 0 | 0 |
| Runs tests in CI | **Yes** | No | No |
| Red-team audit passes | **4** | 0 | 0 |
| Untrusted-output fencing | **Yes** | No | No |
| Stdin piping (no temp files) | **Yes** | Temp files | Temp files |

Star counts are a popularity measure, not a quality one — both alternatives predate this
project by months. The rows above are the things that differ in practice.

### Security audits

Four red-team audit passes (adversarial agents run against the source, commissioned by the author — not a third-party certification), the most recent against v1.1.2 with three parallel agents
covering the shell surface, AppleScript escaping, and information disclosure. It found six real
defects, including a tool that silently annulled another tool's scheme allowlist and a
concurrency slot that could leak until the server deadlocked. Every finding is fixed and carries
a regression test. `escapeAS` was verified against 13 string-breakout candidates through real
`osascript` — none escape.

## Permissions

Tools work in three tiers:

- **No permission needed** — clipboard, notifications, URLs, apps, files, displays, Shortcuts. Works immediately.
- **Automation** — browser tabs, frontmost app. macOS prompts once per browser.
- **Accessibility** — keyboard, windows, menus, hide/unhide. Grant once in **System Settings → Privacy & Security → Accessibility**.
- **Screen Recording** — screenshots only. Grant in **System Settings → Privacy & Security → Screen Recording**.

Ask Claude to run `check_permissions` and it will tell you which of these are already
granted, which tools each one unlocks, and exactly which settings pane to open for the
rest. The probes are read-only and never trigger a permission prompt.

When a permission is missing, the server tells you exactly what to do:

```
"Accessibility permission required. Grant access to 'osascript'
in System Settings > Privacy & Security > Accessibility."
```

## Testing

```bash
uv run pytest -m unit          # 97 unit + hypothesis property tests, no macOS side effects
uv run pytest -m integration   # 81 integration tests against the real server
```

The integration suite drives real windows, menus, the clipboard and `screencapture`, so it changes
local machine state (clipboard contents, may press keys, open apps, show notifications) and needs
Accessibility/Automation/Screen Recording permissions granted to whatever runs it (Terminal,
Claude Desktop) for full coverage — cases gated on a missing permission tolerate that outcome
rather than failing. `OSASCRIPT_MCP_FORMAT=toon` (or `json`) re-runs the same suite against the
other output encodings.

Set `OSASCRIPT_MCP_CAPTURE=/path/to/file.jsonl` to have the server append every structured
result to that file as `{"tool": ..., "payload": ...}` — off unless set, no effect on the
response sent to the client. `uv run python bench/replay.py /path/to/file.jsonl` replays a
capture through each encoding and reports token counts per tool, which is how the numbers in
[Output Format](#output-format) were produced.

Set `OSASCRIPT_MCP_ARGS="arg1 arg2"` (shell-quoted, space-separated) to append positional
arguments after the script on every `osascript` invocation. `osascript` exposes these to the
script as `argv` (JXA) / `on run argv` (AppleScript), so a deployment that needs a
host-specific value (a VM name, an account, a path) can put it in an untracked `.env` or the
MCP client's `env` block instead of hardcoding it into a committed `args` array.

<details>
<summary>Security & Architecture</summary>

### Security

- `run_osascript` executes arbitrary code — this is by design. The MCP client (Claude) is the trust boundary.
- Scripts piped via stdin to `/usr/bin/osascript` — no temp files, no TOCTOU race conditions.
- Script size: 50 KB max. Output: 50K chars max, truncated on a UTF-8 character boundary (no mojibake in non-Latin output).
- Error messages sanitized — filesystem paths, tokens, and passwords are stripped.
- Child processes get minimal env: `PATH`, `HOME`, `LANG` only — no API keys or secrets leak.
- URL scheme allowlist — `file://`, `smb://`, `vnc://`, `javascript:` all blocked.
- Handler dispatch is a plain dict keyed by exact tool name — an unknown or forged name never resolves to a handler.
- Externally-sourced text (browser tab titles, window titles, menu items, clipboard) is returned inside an explicit `<untrusted-data>` envelope, so a web page that renames itself cannot smuggle instructions into the model's context.
- `file_open` refuses anything that parses as a URL — `open(1)` resolves URLs as well as paths, so without that check it would quietly annul `open_url`'s scheme allowlist.
- `screenshot` never overwrites an existing file unless `overwrite: true`, and the extension must match the format.
- Every list-building tool strips `|`, CR and LF from app-supplied names, so a crafted window or tab title cannot forge a record.

### Reliability

- Process group kill on timeout — SIGTERM → 2s grace → SIGKILL. No orphaned processes.
- Concurrency semaphore — max 5 simultaneous osascript processes.
- Graceful shutdown on SIGTERM/SIGINT — refuses new tool calls and cancels the stdio server task.
- Error classification — parses macOS error codes (-1728, -1743, -25211) into actionable messages. Supports English and Russian locales.

</details>

## Requirements

- macOS 13+ (Ventura or later)
- Python 3.13+ with [uv](https://docs.astral.sh/uv/)

## License

MIT
