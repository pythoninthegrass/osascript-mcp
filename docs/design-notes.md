# Design notes

Longer "why" explanations that don't fit as 1-2 line code comments. Referenced from
[AGENTS.md](../AGENTS.md); each heading below corresponds to a short pointer comment at that
location in the source.

## File layout

Both modules are organized top-to-bottom into these sections (no inline dividers in the
source — this is the map):

**`executor.py`**: config loading → safe error sanitization → error classifier → core
executor (`_spawn_guarded` and friends) → convenience wrappers (`execute_apple_script`,
`execute_jxa`).

**`server.py`**: result helpers → subprocess helpers → tools: scripting, clipboard,
notifications, URLs, apps → tools: accessibility and UI → tools: browser tabs, displays,
screenshot, `check_permissions` → tool registry (`TOOLS` / `HANDLERS`).

## Config loading (`.env` anchoring)

`_ENV_FILE` in `executor.py` is resolved from the repo root via `Path(__file__).resolve()`,
not from `decouple`'s bare `config`/`AutoConfig` (which walks up from `os.getcwd()`). The
server is launched via `uvx`/`uv run` from arbitrary directories, so a cwd-relative lookup
would miss a `.env` sitting next to the project. `_env()` falls back to plain `os.environ`
when no `.env` file exists, since `RepositoryEnv` requires the file to be present.

## Extra osascript args (`OSASCRIPT_MCP_ARGS`)

`EXTRA_ARGS` in `executor.py` is appended after the script on every `osascript` invocation.
`osascript` exposes trailing positional args to the script as `argv` (JXA) / `on run argv`
(AppleScript), so a deployment that needs a host-specific value (a VM name, an account, a
path) can put it in `OSASCRIPT_MCP_ARGS` — via an untracked `.env` or the MCP client's `env`
block — instead of hardcoding it into a committed `args` array.

## Output format default (`json-min` vs `toon`)

TASK-001.13 measured [TOON](https://github.com/toon-format/toon) against real captured
payloads from this server (not synthetic ones) and it beat minified JSON by only ~13%
overall — under the 15% bar set before looking at the number — and was an outright
regression on small flat arrays like `app_menu`'s menu-item lists (TOON's `[N]:` header
doesn't amortize over short lists). So `json-min` (free, no new failure surface) is the
default in `server.py`; `toon` remains available for large, uniformly tabular payloads, and
`json` for human debugging.

## `KEY_CODES` key naming

`KEY_CODES` in `server.py` is a plain dict — Python dicts don't have the
`KEY_CODES["constructor"]`/`KEY_CODES["__proto__"]` prototype-pollution hazard that a plain
object would have in JS — but the keys are kept identical to the original JS port for parity
with its "Unknown key" test cases.

## Screen Recording denial detection

`screencapture` gives no dedicated exit code or machine-readable signal for a denied Screen
Recording permission. `_SCREENCAPTURE_DENIAL_FRAGMENTS` and `_screenshot_error_result` in
`server.py` match its known stderr text and then confirm against the real TCC state via
`_screen_recording_access()`, since the text match alone isn't reliable enough to act on.
