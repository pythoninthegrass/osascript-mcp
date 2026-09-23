import asyncio
import os
import pytest
import sys
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Must exceed the server's own 30s default script timeout.
CALL_TIMEOUT_S = 40


def pytest_collection_modifyitems(config, items):
    if sys.platform != "darwin":
        skip_marker = pytest.mark.skip(reason="requires macOS")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_marker)


def server_command() -> tuple[str, list[str]]:
    cmd = os.environ.get("OSASCRIPT_MCP_CMD", f"{sys.executable} -m osascript_mcp")
    parts = cmd.split()
    return parts[0], parts[1:]


@asynccontextmanager
async def open_session():
    """One server process per test, to avoid anyio cancel-scope issues from
    sharing a session-scoped stdio_client across tests."""
    command, args = server_command()
    env = {"LANG": "en_US.UTF-8"}
    if "OSASCRIPT_MCP_FORMAT" in os.environ:
        env["OSASCRIPT_MCP_FORMAT"] = os.environ["OSASCRIPT_MCP_FORMAT"]
    params = StdioServerParameters(command=command, args=args, env=env, cwd=str(ROOT))
    errlog = sys.stderr if os.environ.get("DEBUG") else open(os.devnull, "w")
    try:
        async with stdio_client(params, errlog=errlog) as (read, write), ClientSession(read, write) as client:
            await client.initialize()
            yield client
    finally:
        if errlog is not sys.stderr:
            errlog.close()


@pytest.fixture
def session():
    return open_session


async def _osascript(script: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "/usr/bin/osascript",
        "-e",
        script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode().strip()


@pytest.fixture
async def tmp_finder_window():
    """Open a scratch Finder window on /tmp and bring it frontmost, so a global
    keystroke a test sends (Cmd+A, type-ahead select) lands on throwaway /tmp
    contents instead of whatever the user actually has focused (e.g. the Desktop)."""
    window_id = await _osascript(
        'tell application "Finder"\n'
        '  set w to make new Finder window to (POSIX file "/tmp" as alias)\n'
        "  activate\n"
        "  return id of w as string\n"
        "end tell"
    )
    try:
        yield
    finally:
        if window_id:
            await _osascript(f'tell application "Finder" to close window id {window_id}')


async def _finder_window_ids() -> set[str]:
    raw = await _osascript(
        'tell application "Finder"\n'
        "  set idList to id of every window\n"
        '  set AppleScript\'s text item delimiters to ","\n'
        "  set idString to idList as string\n"
        '  set AppleScript\'s text item delimiters to ""\n'
        "  return idString\n"
        "end tell"
    )
    return {part.strip() for part in raw.split(",") if part.strip()}


@pytest.fixture
async def close_new_finder_windows():
    """Snapshot Finder's window ids before the test and close only whatever new
    window id(s) appear after, so a test that triggers something like "New Finder
    Window" doesn't leave a stray window behind or touch the user's own windows."""
    before = await _finder_window_ids()
    yield
    after = await _finder_window_ids()
    for window_id in after - before:
        await _osascript(f'tell application "Finder" to close window id {window_id}')
