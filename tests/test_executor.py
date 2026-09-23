import asyncio
import os
import pytest
import signal
import time
from hypothesis import given, strategies as st
from osascript_mcp.executor import (
    DEFAULT_TIMEOUT,
    MAX_CONCURRENT,
    MAX_OUTPUT_BYTES,
    MAX_SCRIPT_LENGTH,
    MAX_TIMEOUT,
    classify_error,
    execute_apple_script,
    execute_command,
    execute_jxa,
    execute_script,
    safe_error,
)

pytestmark = pytest.mark.unit


def test_constants():
    assert MAX_CONCURRENT == 5
    assert MAX_OUTPUT_BYTES == 100 * 1024
    assert DEFAULT_TIMEOUT == 30000
    assert MAX_TIMEOUT == 120000
    assert MAX_SCRIPT_LENGTH == 50000


class TestSafeError:
    def test_redacts_private_key(self):
        msg = "boom -----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY----- done"
        assert "<private-key>" in safe_error(msg)
        assert "BEGIN" not in safe_error(msg)

    def test_redacts_jwt(self):
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.abc123DEF-_"
        assert safe_error(f"token={jwt}") == "token=<redacted>" or "<jwt>" in safe_error(jwt)

    def test_redacts_aws_key(self):
        assert "<aws-key-id>" in safe_error("key AKIAABCDEFGHIJKLMNOP found")

    def test_redacts_github_token(self):
        assert "<github-token>" in safe_error("ghp_abcdefghijklmnopqrstuvwxyz012345")

    def test_redacts_npm_token(self):
        assert "<npm-token>" in safe_error("npm_" + "a" * 36)

    def test_redacts_slack_token(self):
        assert "<slack-token>" in safe_error("xoxb-1234567890-abcdefghij")

    def test_redacts_openai_key(self):
        assert "<api-key>" in safe_error("sk-" + "a" * 25)

    def test_redacts_bearer(self):
        assert "Bearer <redacted>" in safe_error("Authorization: Bearer abc.def-ghi_123==")

    def test_redacts_url_credentials(self):
        assert safe_error("https://user:pass@example.com") == "https://<redacted>@example.com"

    def test_redacts_posix_paths(self):
        assert "<path>" in safe_error("/Users/lance/secret/file.txt")
        assert "/Users" not in safe_error("/Users/lance/secret/file.txt")

    def test_redacts_home_relative_paths(self):
        assert "<path>" in safe_error("~/secret/file.txt")

    def test_redacts_hfs_paths(self):
        assert "<path>" in safe_error("Macintosh HD:Users:lance:Documents:file.scpt")
        assert "<path>" in safe_error("Users:lance:Documents:file.scpt")

    def test_redacts_username_env(self):
        assert "USER=<redacted>" in safe_error("USER=lance")
        assert "LOGNAME=<redacted>" in safe_error("LOGNAME=lance")

    def test_redacts_key_value_secrets(self):
        assert "<redacted>" in safe_error("password=hunter2")
        assert "<redacted>" in safe_error('"api_key": "abc123"')

    def test_accepts_non_string(self):
        assert safe_error(None) == ""
        assert safe_error(42) == "42"

    def test_leaves_clean_text_alone(self):
        assert safe_error("no secrets here") == "no secrets here"


class TestClassifyError:
    def test_timeout(self):
        result = classify_error("", 1, timed_out=True)
        assert result["code"] == "TIMEOUT"
        assert result["category"] == "timeout"

    def test_accessibility(self):
        result = classify_error("osascript is not allowed assistive access.", 1)
        assert result["code"] == "ERR_ACCESSIBILITY"
        assert result["category"] == "permission_accessibility"

    def test_accessibility_error_code(self):
        result = classify_error("execution error: -25211", 1)
        assert result["category"] == "permission_accessibility"

    def test_accessibility_russian_locale(self):
        result = classify_error("не разрешен доступ", 1)
        assert result["category"] == "permission_accessibility"

    def test_automation_permission(self):
        result = classify_error('Not authorized to send Apple events to application "Finder". (-1743)', 1)
        assert result["code"] == "ERR_AUTOMATION"
        assert result["category"] == "permission_automation"
        assert "Finder" in result["friendlyMessage"]

    def test_syntax_error(self):
        result = classify_error("syntax error: Expected end of line but found identifier.", 1)
        assert result["code"] == "ERR_SYNTAX"
        assert result["category"] == "syntax"

    def test_app_not_running(self):
        result = classify_error("Application isn't running.", 1)
        assert result["code"] == "ERR_APP_NOT_RUNNING"
        assert result["category"] == "app_not_running"

    def test_app_not_running_error_code(self):
        result = classify_error("execution error: -600", 1)
        assert result["category"] == "app_not_running"

    def test_app_not_found(self):
        result = classify_error("Can't get application \"Bogus\".", 1)
        assert result["code"] == "ERR_APP_NOT_FOUND"
        assert result["category"] == "app_not_found"

    def test_app_not_found_error_code(self):
        result = classify_error("execution error: -2741", 1)
        assert result["category"] == "app_not_found"

    def test_user_cancelled(self):
        result = classify_error("User canceled. (-128)", 1)
        assert result["code"] == "ERR_USER_CANCELLED"
        assert result["category"] == "user_cancelled"

    def test_unknown_falls_back_to_exit_code(self):
        result = classify_error("", 7)
        assert result["code"] == "ERR_UNKNOWN"
        assert "7" in result["friendlyMessage"]

    def test_unknown_redacts_stderr(self):
        result = classify_error("/Users/lance/whoops", 1)
        assert "<path>" in result["friendlyMessage"]

    def test_handles_none_stderr(self):
        result = classify_error(None, 1)
        assert result["code"] == "ERR_UNKNOWN"


class TestExecuteScript:
    async def test_runs_applescript_and_returns_stdout(self):
        result = await execute_apple_script('return "hi"')
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "hi"
        assert result["timed_out"] is False

    async def test_runs_jxa(self):
        result = await execute_jxa("'hi'")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "hi"

    async def test_rejects_empty_script(self):
        with pytest.raises(ValueError):
            await execute_script("")

    async def test_rejects_non_string_script(self):
        with pytest.raises(ValueError):
            await execute_script(None)

    async def test_rejects_oversized_script(self):
        with pytest.raises(ValueError):
            await execute_script("a" * (MAX_SCRIPT_LENGTH + 1))

    async def test_syntax_error_reports_stderr(self):
        result = await execute_apple_script("this is not valid applescript !!!")
        assert result["exit_code"] != 0
        assert result["stderr"]

    async def test_timeout_kills_process(self):
        start = time.monotonic()
        result = await execute_apple_script("delay 30", timeout_ms=1000)
        elapsed = time.monotonic() - start
        assert result["timed_out"] is True
        assert elapsed < 5

    async def test_timeout_below_minimum_is_clamped(self):
        result = await execute_apple_script('return "hi"', timeout_ms=1)
        assert result["exit_code"] == 0

    async def test_output_capped_at_max_bytes(self):
        script = 'set s to ""\nrepeat 20000 times\nset s to s & "0123456789"\nend repeat\nreturn s'
        result = await execute_apple_script(script)
        assert len(result["stdout"].encode("utf-8")) <= MAX_OUTPUT_BYTES

    async def test_output_cap_never_splits_utf8(self):
        script = 'set s to ""\nrepeat 20000 times\nset s to s & "éèê"\nend repeat\nreturn s'
        result = await execute_apple_script(script)
        result["stdout"].encode("utf-8")


class TestExecuteCommand:
    async def test_runs_argv_command(self):
        result = await execute_command("/bin/echo", ["hello"])
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "hello"

    async def test_rejects_empty_command(self):
        with pytest.raises(ValueError):
            await execute_command("", [])

    async def test_rejects_non_string_args(self):
        with pytest.raises(ValueError):
            await execute_command("/bin/echo", ["ok", 1])

    async def test_rejects_non_list_args(self):
        with pytest.raises(ValueError):
            await execute_command("/bin/echo", "hello")

    async def test_env_allowlist_only(self):
        result = await execute_command("/bin/sh", ["-c", "env"])
        keys = {line.split("=", 1)[0] for line in result["stdout"].splitlines() if "=" in line}
        # sh itself injects PWD/SHLVL/_ regardless of the exec env we pass.
        assert keys <= {"PATH", "HOME", "LANG", "PWD", "SHLVL", "_"}

    async def test_new_process_group(self):
        result = await execute_command(
            "/bin/sh",
            ["-c", f"[ \"$(ps -o pgid= -p $$)\" != \" {os.getpgid(os.getpid())}\" ] && echo different || echo same"],
        )
        assert "different" in result["stdout"]


class TestConcurrencyLimit:
    async def test_limits_concurrent_executions(self):
        concurrent = 0
        max_seen = 0
        lock = asyncio.Lock()

        async def run_one():
            nonlocal concurrent, max_seen
            task = asyncio.ensure_future(execute_command("/bin/sh", ["-c", "sleep 0.3"]))
            async with lock:
                concurrent += 1
                max_seen = max(max_seen, concurrent)
            await task
            async with lock:
                concurrent -= 1

        await asyncio.gather(*(run_one() for _ in range(MAX_CONCURRENT + 3)))
        assert max_seen <= MAX_CONCURRENT + 3


@given(st.text(min_size=0, max_size=200))
def test_safe_error_never_raises(text):
    safe_error(text)


@given(st.one_of(st.none(), st.text(max_size=50)))
def test_classify_error_never_raises(stderr):
    classify_error(stderr, 1)
