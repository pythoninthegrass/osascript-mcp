import asyncio
import os
import re
import shlex
import signal
from decouple import Config, RepositoryEnv
from pathlib import Path

MAX_CONCURRENT = 5
MAX_OUTPUT_BYTES = 100 * 1024  # textResult truncates at 50K chars, no need for 1 MB
DEFAULT_TIMEOUT = 30000
MAX_TIMEOUT = 120000
MAX_SCRIPT_LENGTH = 50000
KILL_GRACE_SECONDS = 2

_semaphore = asyncio.Semaphore(MAX_CONCURRENT)

# RepositoryEnv anchored on the repo root (not the bare `decouple.config`/AutoConfig, which
# walks up from os.getcwd()) so a .env is found regardless of the server's cwd — it's
# launched via `uvx`/`uv run` from arbitrary directories. Falls back to plain os.environ
# when there's no .env file to load, since RepositoryEnv requires the file to exist.
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
_config = Config(RepositoryEnv(_ENV_FILE)) if _ENV_FILE.exists() else None


def _env(key: str, default=None):
    return _config(key, default=default) if _config is not None else os.environ.get(key, default)


# Extra positional args appended after the script, e.g. `OSASCRIPT_MCP_ARGS="vm-01 admin"`.
# osascript passes these through as `argv` (JXA) / `on run argv` (AppleScript) parameters,
# so host-specific values (VM name, account, etc.) can live in an untracked .env instead of
# being hardcoded into a committed MCP client config.
EXTRA_ARGS = shlex.split(_env("OSASCRIPT_MCP_ARGS", "") or "")

# ---------------------------------------------------------------------------
# Safe error sanitization
# ---------------------------------------------------------------------------
_PRIVATE_KEY_RE = re.compile(r"-----BEGIN[\s\S]*?-----END[^-]*-----")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
_AWS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
_GITHUB_TOKEN_RE = re.compile(r"\b(?:gh[pousr]|github_pat)_[A-Za-z0-9_]{20,}")
_NPM_TOKEN_RE = re.compile(r"\bnpm_[A-Za-z0-9]{30,}")
_SLACK_TOKEN_RE = re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")
_API_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")
_BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*")
_URL_CREDENTIALS_RE = re.compile(r"//[^/\s:@]+:[^/\s@]+@")
_POSIX_PATH_RE = re.compile(
    r"(?:/Users|/home|/var|/private|/tmp|/opt|/etc|/usr|/Applications|/Library|/System|/Volumes)/[^\s'\",;)}\]>]*"
)
_HOME_PATH_RE = re.compile(r"~/[^\s'\",;)}\]>]*")
_HFS_NAMED_VOLUME_RE = re.compile(r"\b[A-Za-z][\w ]*:Users:[^\s'\"]*")
_HFS_USERS_RE = re.compile(r"\bUsers:[^\s'\"]*")
_USERNAME_ENV_RE = re.compile(r"\b(USER|LOGNAME|USERNAME)=\S+")
_SECRET_KV_RE = re.compile(
    r"([A-Za-z_]*(?:password|passwd|token|secret|api[_-]?key|apikey|credential)[A-Za-z_]*)"
    r"[\"']?\s*[=:]\s*[\"']?[^\s\"',;)}\]>]+",
    re.IGNORECASE,
)


def safe_error(error) -> str:
    msg = error if isinstance(error, str) else ("" if error is None else str(error))

    msg = _PRIVATE_KEY_RE.sub("<private-key>", msg)
    msg = _JWT_RE.sub("<jwt>", msg)
    msg = _AWS_KEY_RE.sub("<aws-key-id>", msg)
    msg = _GITHUB_TOKEN_RE.sub("<github-token>", msg)
    msg = _NPM_TOKEN_RE.sub("<npm-token>", msg)
    msg = _SLACK_TOKEN_RE.sub("<slack-token>", msg)
    msg = _API_KEY_RE.sub("<api-key>", msg)
    msg = _BEARER_RE.sub("Bearer <redacted>", msg)

    msg = _URL_CREDENTIALS_RE.sub("//<redacted>@", msg)

    msg = _POSIX_PATH_RE.sub("<path>", msg)
    msg = _HOME_PATH_RE.sub("<path>", msg)
    msg = _HFS_NAMED_VOLUME_RE.sub("<path>", msg)
    msg = _HFS_USERS_RE.sub("<path>", msg)

    msg = _USERNAME_ENV_RE.sub(r"\1=<redacted>", msg)

    msg = _SECRET_KV_RE.sub(r"\1=<redacted>", msg)

    return msg


# ---------------------------------------------------------------------------
# Error classifier
# ---------------------------------------------------------------------------
def classify_error(stderr, exit_code, timed_out: bool = False) -> dict:
    s = (stderr or "").lower()

    if timed_out:
        return {
            "code": "TIMEOUT",
            "category": "timeout",
            "friendlyMessage": "Script exceeded timeout",
            "remediation": "Reduce script complexity or increase the timeout parameter.",
        }

    if (
        "not allowed assistive access" in s
        or "not allowed to send keystrokes" in s
        or "не разрешен" in s
        or "-25211" in s
        or "-1719" in s
        or ("-1728" in s and "assistive" in s)
    ):
        return {
            "code": "ERR_ACCESSIBILITY",
            "category": "permission_accessibility",
            "friendlyMessage": "Accessibility permission required. Grant access in System Settings > Privacy & Security > Accessibility.",
            "remediation": "Open System Settings > Privacy & Security > Accessibility and add/enable the calling application.",
        }

    if "-1743" in s:
        app_match = re.search(r'application (?:process )?["“”]?(.+?)["“”]?(?:\.|$)', stderr or "", re.IGNORECASE)
        app = safe_error(app_match.group(1)) if app_match else "the target app"
        return {
            "code": "ERR_AUTOMATION",
            "category": "permission_automation",
            "friendlyMessage": f"Grant Automation permission for {app} in System Settings > Privacy & Security > Automation",
            "remediation": f"Open System Settings > Privacy & Security > Automation and allow the calling application to control {app}.",
        }

    if "syntax error" in s:
        return {
            "code": "ERR_SYNTAX",
            "category": "syntax",
            "friendlyMessage": "AppleScript syntax error — check quotes and 'end tell' blocks",
            "remediation": "Review the script for unmatched quotes, missing 'end tell', or invalid keywords.",
        }

    if "application isn't running" in s or "-600" in s:
        return {
            "code": "ERR_APP_NOT_RUNNING",
            "category": "app_not_running",
            "friendlyMessage": "Application is not running. Use open_app to launch it first.",
            "remediation": "Launch the target application before running the script.",
        }

    if "can't get application" in s or "-2741" in s:
        return {
            "code": "ERR_APP_NOT_FOUND",
            "category": "app_not_found",
            "friendlyMessage": "Application not found or not scriptable",
            "remediation": "Verify the application name is correct and that it supports AppleScript/JXA.",
        }

    if "-128" in s:
        return {
            "code": "ERR_USER_CANCELLED",
            "category": "user_cancelled",
            "friendlyMessage": "User cancelled the action",
            "remediation": "The user dismissed a dialog or cancelled the operation.",
        }

    return {
        "code": "ERR_UNKNOWN",
        "category": "unknown",
        "friendlyMessage": safe_error(stderr or f"Script exited with code {exit_code}"),
        "remediation": "Check the stderr output for details.",
    }


# ---------------------------------------------------------------------------
# Core executor
# ---------------------------------------------------------------------------
async def _read_capped_stream(stream: asyncio.StreamReader) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await stream.read(65536)
        if not chunk:
            break
        if total < MAX_OUTPUT_BYTES:
            remaining = MAX_OUTPUT_BYTES - total
            chunks.append(chunk[:remaining] if len(chunk) > remaining else chunk)
        total += len(chunk)
    return b"".join(chunks)


def _decode_capped(data: bytes) -> str:
    # Drop a dangling multi-byte sequence at the cap boundary instead of
    # turning it into U+FFFD.
    while data:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as err:
            data = data[: err.start]
    return ""


async def _spawn_guarded(command: str, args: list[str], stdin_data: str | None, timeout_ms: float) -> dict:
    effective_timeout = min(max(timeout_ms, 1000), MAX_TIMEOUT) / 1000

    async with _semaphore:
        process = await asyncio.create_subprocess_exec(
            command,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={
                "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
                "HOME": os.environ.get("HOME", "/tmp"),
                "LANG": "en_US.UTF-8",
            },
            start_new_session=True,
        )

        stdin_bytes = stdin_data.encode("utf-8") if stdin_data is not None else None

        async def communicate():
            stdout_task = asyncio.ensure_future(_read_capped_stream(process.stdout))
            stderr_task = asyncio.ensure_future(_read_capped_stream(process.stderr))
            if stdin_bytes is not None:
                process.stdin.write(stdin_bytes)
            try:
                process.stdin.close()
            except Exception:
                pass
            stdout_bytes, stderr_bytes = await asyncio.gather(stdout_task, stderr_task)
            exit_code = await process.wait()
            return stdout_bytes, stderr_bytes, exit_code

        try:
            stdout_bytes, stderr_bytes, exit_code = await asyncio.wait_for(communicate(), timeout=effective_timeout)
            return {
                "stdout": _decode_capped(stdout_bytes),
                "stderr": _decode_capped(stderr_bytes),
                "exit_code": exit_code,
                "timed_out": False,
            }
        except TimeoutError:
            pgid = os.getpgid(process.pid)
            try:
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(process.wait(), timeout=KILL_GRACE_SECONDS)
            except TimeoutError:
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    await asyncio.wait_for(process.wait(), timeout=KILL_GRACE_SECONDS)
                except TimeoutError:
                    pass
            return {"stdout": "", "stderr": "", "exit_code": process.returncode or 1, "timed_out": True}


async def execute_script(script, language: str = "applescript", timeout_ms: float = DEFAULT_TIMEOUT) -> dict:
    if not script or not isinstance(script, str):
        raise ValueError("script must be a non-empty string")
    if len(script) > MAX_SCRIPT_LENGTH:
        raise ValueError(f"Script length {len(script)} exceeds maximum of {MAX_SCRIPT_LENGTH} characters")

    args = []
    if language == "javascript":
        args.extend(["-l", "JavaScript"])
    args.append("-")  # read the script from stdin
    args.extend(EXTRA_ARGS)

    return await _spawn_guarded("/usr/bin/osascript", args, script, timeout_ms)


async def execute_command(command: str, args: list[str], timeout_ms: float = DEFAULT_TIMEOUT) -> dict:
    if not isinstance(command, str) or not command:
        raise ValueError("command must be a non-empty string")
    if not isinstance(args, list) or any(not isinstance(a, str) for a in args):
        raise ValueError("args must be an array of strings")
    return await _spawn_guarded(command, args, None, timeout_ms)


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------
async def execute_apple_script(script, timeout_ms: float = DEFAULT_TIMEOUT) -> dict:
    return await execute_script(script, "applescript", timeout_ms)


async def execute_jxa(script, timeout_ms: float = DEFAULT_TIMEOUT) -> dict:
    return await execute_script(script, "javascript", timeout_ms)
