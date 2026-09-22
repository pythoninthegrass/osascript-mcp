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
    params = StdioServerParameters(command=command, args=args, env={"LANG": "en_US.UTF-8"}, cwd=str(ROOT))
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
