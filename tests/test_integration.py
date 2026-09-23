import asyncio
import json
import os
import pytest
import re
import time
import toon_format
from conftest import CALL_TIMEOUT_S

pytestmark = pytest.mark.integration

OUTPUT_FORMAT = os.environ.get("OSASCRIPT_MCP_FORMAT", "json-min").lower()


def text(result):
    return result.content[0].text


def parse_result(body: str):
    """Decode a server-encoded payload per OSASCRIPT_MCP_FORMAT, matching server.encode_payload."""
    if OUTPUT_FORMAT in ("json", "json-min"):
        return json.loads(body)
    return toon_format.decode(body)


async def call(client, name, arguments=None):
    return await asyncio.wait_for(client.call_tool(name, arguments or {}), timeout=CALL_TIMEOUT_S)


async def safari_running(client) -> bool:
    r = await call(
        client,
        "run_osascript",
        {"script": 'tell application "System Events" to return (exists process "Safari") as text'},
    )
    return text(r).strip() == "true"


def strip_untrusted_envelope(body: str) -> str:
    body = re.sub(r"^[\s\S]*?<untrusted-data[^>]*>", "", body)
    body = re.sub(r"</untrusted-data>[\s\S]*$", "", body)
    return body


async def test_initialize_succeeds(session):
    # open_session() already calls ClientSession.initialize() before yielding;
    # entering the context manager without raising is the assertion.
    async with session() as client:
        assert client is not None


async def test_tools_list_returns_18_tools(session):
    async with session() as client:
        tools = await client.list_tools()
        assert len(tools.tools) == 18


async def test_run_osascript_basic_applescript(session):
    async with session() as client:
        r = await call(client, "run_osascript", {"script": "return 2 + 2"})
        assert text(r) == "4"


async def test_run_osascript_jxa(session):
    async with session() as client:
        r = await call(client, "run_osascript", {"script": "40 + 2", "language": "javascript"})
        assert text(r) == "42"


async def test_run_osascript_empty_script_rejected(session):
    async with session() as client:
        r = await call(client, "run_osascript", {"script": ""})
        assert r.is_error is True


async def test_run_osascript_oversized_script_rejected(session):
    async with session() as client:
        r = await call(client, "run_osascript", {"script": "x" * 60000})
        assert r.is_error is True


async def test_clipboard_round_trip(session):
    async with session() as client:
        await call(client, "set_clipboard", {"content": "mcp-test-123"})
        r = await call(client, "get_clipboard")
        assert "mcp-test-123" in text(r)
        assert "<untrusted-data" in text(r)


async def test_open_url_https_accepted(session):
    async with session() as client:
        r = await call(client, "open_url", {"url": "https://example.com"})
        assert not r.is_error


async def test_open_url_file_scheme_rejected(session):
    async with session() as client:
        r = await call(client, "open_url", {"url": "file:///etc/passwd"})
        assert r.is_error is True


async def test_open_url_smb_scheme_rejected(session):
    async with session() as client:
        r = await call(client, "open_url", {"url": "smb://evil.com/share"})
        assert r.is_error is True


async def test_open_app_finder(session):
    async with session() as client:
        r = await call(client, "open_app", {"name": "Finder"})
        assert not r.is_error


async def test_open_app_nonexistent_rejected(session):
    async with session() as client:
        r = await call(client, "open_app", {"name": "ThisAppDoesNotExist12345"})
        assert r.is_error is True


async def test_get_frontmost_app_returns_name(session):
    async with session() as client:
        r = await call(client, "get_frontmost_app")
        assert "name" in text(r)


async def test_manage_windows_list_or_accessibility_error(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "list"})
        assert not r.is_error or "Accessibility" in text(r)


async def test_app_menu_list_finder_or_accessibility_error(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "list", "app": "Finder"})
        assert not r.is_error or "Accessibility" in text(r)


async def test_press_key_invalid_key_rejected(session):
    async with session() as client:
        r = await call(client, "press_key", {"key": "nonexistent_key_xyz"})
        assert r.is_error is True


async def test_unknown_tool_name_rejected(session):
    async with session() as client:
        r = await call(client, "constructor")
        assert r.is_error is True


async def test_type_text_empty_rejected(session):
    async with session() as client:
        r = await call(client, "type_text", {"text": ""})
        assert r.is_error is True


async def test_type_text_over_500_chars_rejected(session):
    async with session() as client:
        r = await call(client, "type_text", {"text": "a" * 501})
        assert r.is_error is True


async def test_type_text_valid_or_accessibility_error(session, tmp_finder_window):
    async with session() as client:
        r = await call(client, "type_text", {"text": "hello"})
        assert not r.is_error or "Accessibility" in text(r)


async def test_press_key_named_key_escape_or_accessibility_error(session):
    async with session() as client:
        r = await call(client, "press_key", {"key": "escape"})
        assert not r.is_error or "Accessibility" in text(r)


async def test_press_key_char_with_command_modifier_or_accessibility_error(session, tmp_finder_window):
    async with session() as client:
        r = await call(client, "press_key", {"key": "a", "modifiers": ["command"]})
        assert not r.is_error or "Accessibility" in text(r)


async def test_press_key_invalid_modifier_rejected(session):
    async with session() as client:
        r = await call(client, "press_key", {"key": "a", "modifiers": ["super"]})
        assert r.is_error is True


async def test_get_browser_tabs_invalid_browser_rejected(session):
    async with session() as client:
        r = await call(client, "get_browser_tabs", {"browser": "firefox"})
        assert r.is_error is True


async def test_get_browser_tabs_safari(session):
    async with session() as client:
        if not await safari_running(client):
            pytest.skip("Safari is not running")
        r = await call(client, "get_browser_tabs", {"browser": "safari"})
        body = text(r)
        assert not r.is_error or "not running" in body or "Automation" in body or re.search(r"timeout", body, re.I)


async def test_browser_tabs_marked_untrusted(session):
    async with session() as client:
        if not await safari_running(client):
            pytest.skip("Safari is not running")
        r = await call(client, "get_browser_tabs", {"browser": "safari"})
        assert r.is_error or "<untrusted-data" in text(r)


async def test_manage_windows_invalid_action_rejected(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "destroy"})
        assert r.is_error is True


async def test_manage_windows_move_without_position_rejected(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "move", "app": "Finder"})
        assert r.is_error is True


async def test_manage_windows_resize_below_minimum_rejected(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "resize", "app": "Finder", "size": {"width": 50, "height": 50}})
        assert r.is_error is True


async def test_manage_windows_non_integer_window_index_rejected(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "list", "app": "Finder", "window": 1.5})
        assert r.is_error is True


async def test_app_menu_missing_app_rejected(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "list", "app": ""})
        assert r.is_error is True


async def test_app_menu_click_without_menu_path_rejected(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "click", "app": "Finder"})
        assert r.is_error is True


async def test_app_menu_click_with_menu_path_length_1_rejected(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "click", "app": "Finder", "menu_path": ["File"]})
        assert r.is_error is True


async def test_app_menu_invalid_action_rejected(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "hover", "app": "Finder"})
        assert r.is_error is True


async def test_app_menu_click_by_position_or_accessibility_error(session, close_new_finder_windows):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "click", "app": "Finder", "menu_path": ["File", 1]})
        assert not r.is_error or "Accessibility" in text(r) or "not found" in text(r).lower()
        assert "Internal error" not in text(r)


async def test_app_menu_list_by_position_or_accessibility_error(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "list", "app": "Finder", "menu_path": [1]})
        assert not r.is_error or "Accessibility" in text(r) or "not found" in text(r).lower()
        assert "Internal error" not in text(r)


async def test_set_clipboard_missing_content_rejected(session):
    async with session() as client:
        r = await call(client, "set_clipboard", {})
        assert r.is_error is True


async def test_set_clipboard_number_instead_of_string_rejected(session):
    async with session() as client:
        r = await call(client, "set_clipboard", {"content": 12345})
        assert r.is_error is True


async def test_run_osascript_invalid_language_rejected(session):
    async with session() as client:
        r = await call(client, "run_osascript", {"script": "return 1", "language": "python"})
        assert r.is_error is True


async def test_run_osascript_syntax_error_returns_is_error(session):
    async with session() as client:
        r = await call(client, "run_osascript", {"script": "this is not valid applescript @@##$$"})
        assert r.is_error is True


async def test_run_osascript_timeout_enforcement(session):
    async with session() as client:
        start = time.monotonic()
        r = await call(client, "run_osascript", {"script": "delay 10", "timeout": 2})
        elapsed_ms = (time.monotonic() - start) * 1000
        assert r.is_error is True
        assert elapsed_ms < 5000


async def test_open_url_mailto_scheme_accepted(session):
    async with session() as client:
        r = await call(client, "open_url", {"url": "mailto:test@example.com"})
        assert not r.is_error


async def test_open_url_javascript_scheme_rejected(session):
    async with session() as client:
        r = await call(client, "open_url", {"url": "javascript:alert(1)"})
        assert r.is_error is True


async def test_screenshot_fullscreen(session):
    async with session() as client:
        r = await call(
            client,
            "screenshot",
            {"mode": "fullscreen", "path": "/tmp/mcp-test-screenshot.png", "overwrite": True},
        )
        assert not r.is_error or "permission" in text(r)


async def test_screenshot_region_without_coords_rejected(session):
    async with session() as client:
        r = await call(client, "screenshot", {"mode": "region"})
        assert r.is_error is True


async def test_screenshot_window_mode_nonexistent_app_rejected(session):
    async with session() as client:
        r = await call(client, "screenshot", {"mode": "window", "app": "NonExistentApp12345"})
        assert r.is_error is True


async def test_app_visibility_invalid_action_rejected(session):
    async with session() as client:
        r = await call(client, "app_visibility", {"action": "minimize", "app": "Finder"})
        assert r.is_error is True


async def test_app_visibility_missing_app_rejected(session):
    async with session() as client:
        r = await call(client, "app_visibility", {"action": "hide", "app": ""})
        assert r.is_error is True


async def test_app_visibility_invalid_app_name_rejected(session):
    async with session() as client:
        r = await call(client, "app_visibility", {"action": "hide", "app": "Bad/App"})
        assert r.is_error is True


async def test_app_visibility_hide_unhide_finder(session):
    async with session() as client:
        r_hide = await call(client, "app_visibility", {"action": "hide", "app": "Finder"})
        assert not r_hide.is_error or "ccessib" in text(r_hide)
        r_unhide = await call(client, "app_visibility", {"action": "unhide", "app": "Finder"})
        assert not r_unhide.is_error or "ccessib" in text(r_unhide)


async def test_file_open_missing_path_rejected(session):
    async with session() as client:
        r = await call(client, "file_open", {"path": ""})
        assert r.is_error is True


async def test_file_open_tmp_succeeds(session):
    async with session() as client:
        r = await call(client, "file_open", {"path": "/tmp"})
        assert not r.is_error


async def test_file_open_invalid_app_name_rejected(session):
    async with session() as client:
        r = await call(client, "file_open", {"path": "/tmp", "app": "Bad/App"})
        assert r.is_error is True


async def test_run_shortcut_list_succeeds(session):
    async with session() as client:
        r = await call(client, "run_shortcut", {"action": "list"})
        assert not r.is_error


async def test_run_shortcut_invalid_action_rejected(session):
    async with session() as client:
        r = await call(client, "run_shortcut", {"action": "delete"})
        assert r.is_error is True


async def test_run_shortcut_run_without_name_rejected(session):
    async with session() as client:
        r = await call(client, "run_shortcut", {"action": "run"})
        assert r.is_error is True


async def test_run_shortcut_run_with_empty_name_rejected(session):
    async with session() as client:
        r = await call(client, "run_shortcut", {"action": "run", "name": ""})
        assert r.is_error is True


async def test_screenshot_unknown_mode_rejected(session):
    async with session() as client:
        r = await call(client, "screenshot", {"mode": "everything"})
        assert r.is_error is True


async def test_screenshot_unknown_format_rejected(session):
    async with session() as client:
        r = await call(client, "screenshot", {"format": "bmp"})
        assert r.is_error is True


async def test_screenshot_window_clipboard_honours_mode(session):
    async with session() as client:
        r = await call(client, "screenshot", {"mode": "window", "app": "NonExistentApp12345", "clipboard": True})
        assert r.is_error is True


async def test_file_open_leading_dash_path_is_filename(session):
    async with session() as client:
        r = await call(client, "file_open", {"path": "/tmp/-h"})
        assert r.is_error is True
        assert "does not exist" in text(r)


async def test_manage_windows_schema_has_no_dead_display_param(session):
    async with session() as client:
        tools = await client.list_tools()
        schema = next(t for t in tools.tools if t.name == "manage_windows").input_schema
        assert "display" not in schema.get("properties", {})


async def test_type_text_restores_clipboard(session):
    async with session() as client:
        await call(client, "set_clipboard", {"content": "sentinel-clip-42"})
        r_type = await call(client, "type_text", {"text": "x"})
        r_clip = await call(client, "get_clipboard")
        if not r_type.is_error:
            assert "sentinel-clip-42" in text(r_clip)


async def test_cgwindowlist_bridges_to_real_array(session):
    async with session() as client:
        r = await call(
            client,
            "run_osascript",
            {
                "language": "javascript",
                "script": (
                    'ObjC.import("CoreGraphics");'
                    "var wins = ObjC.deepUnwrap(ObjC.castRefToObject("
                    "$.CGWindowListCopyWindowInfo($.kCGWindowListOptionOnScreenOnly, 0)));"
                    "JSON.stringify({ isArray: Array.isArray(wins), len: wins.length });"
                ),
            },
        )
        parsed = json.loads(text(r))
        assert parsed["isArray"] is True
        assert parsed["len"] > 0


async def test_screenshot_window_mode_resolves_frontmost_app(session):
    async with session() as client:
        front = await call(client, "get_frontmost_app")
        front_name = parse_result(text(front))["name"]
        r = await call(
            client,
            "screenshot",
            {"mode": "window", "app": front_name, "path": "/tmp/mcp-test-window.png", "overwrite": True},
        )
        assert not r.is_error or "No windows found" in text(r) or "permission" in text(r)


async def test_file_open_rejects_url_schemes(session):
    async with session() as client:
        r = await call(client, "file_open", {"path": "smb://attacker.example/share"})
        assert r.is_error is True
        assert "open_url" in text(r)


async def test_file_open_rejects_relative_path(session):
    async with session() as client:
        r = await call(client, "file_open", {"path": "relative/path.txt"})
        assert r.is_error is True


async def test_screenshot_refuses_to_overwrite_by_default(session):
    async with session() as client:
        r = await call(
            client,
            "screenshot",
            {
                "mode": "region",
                "region": {"x": 0, "y": 0, "width": 100, "height": 100},
                "path": "/tmp/mcp-test-screenshot.png",
            },
        )
        assert r.is_error is True
        assert "overwrite" in text(r)


async def test_screenshot_rejects_mismatched_extension(session):
    async with session() as client:
        r = await call(client, "screenshot", {"mode": "fullscreen", "path": "/tmp/mcp-test.zshrc"})
        assert r.is_error is True


@pytest.mark.parametrize("proto", ["constructor", "__proto__"])
async def test_press_key_rejects_prototype_chain_names(session, proto):
    async with session() as client:
        r = await call(client, "press_key", {"key": proto})
        assert r.is_error is True
        assert "Unknown key" in text(r)


async def test_manage_windows_rejects_non_finite_position(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "move", "app": "Finder", "position": {"x": 1e999, "y": 0}})
        assert r.is_error is True


async def test_manage_windows_rejects_non_finite_size(session):
    async with session() as client:
        r = await call(
            client,
            "manage_windows",
            {"action": "resize", "app": "Finder", "size": {"width": 1e999, "height": 500}},
        )
        assert r.is_error is True


async def test_window_list_reports_parseable_geometry(session):
    async with session() as client:
        r = await call(client, "manage_windows", {"action": "list", "app": "Finder"})
        body = text(r)
        if "Accessibility" in body:
            return
        parsed = parse_result(strip_untrusted_envelope(body))
        windows = parsed["windows"]
        assert windows == [] or all(
            isinstance(w["width"], (int, float)) and isinstance(w["height"], (int, float)) and w["width"] > 0 for w in windows
        )


async def test_app_menu_rejects_non_string_menu_path_entry(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "click", "app": "Finder", "menu_path": ["File", {"a": 1}]})
        assert r.is_error is True
        assert "Internal error" not in text(r)


async def test_app_menu_rejects_out_of_range_position_entry(session):
    async with session() as client:
        r = await call(client, "app_menu", {"action": "click", "app": "Finder", "menu_path": ["File", 0]})
        assert r.is_error is True
        assert "Internal error" not in text(r)


async def test_app_visibility_rejects_colon_in_app_name(session):
    async with session() as client:
        r = await call(client, "app_visibility", {"action": "hide", "app": "Disk:Applications:Foo"})
        assert r.is_error is True


async def test_set_clipboard_limits_escaped_length(session):
    async with session() as client:
        r = await call(client, "set_clipboard", {"content": "\\" * 30000})
        assert r.is_error is True
        assert "Internal error" not in text(r)


async def test_run_shortcut_passes_input_without_arg_order_breakage(session):
    async with session() as client:
        r = await call(client, "run_shortcut", {"action": "run", "name": "NoSuchShortcut12345", "input": "hello"})
        assert "unexpected argument" not in text(r)


async def test_run_shortcut_rejects_non_string_input(session):
    async with session() as client:
        r = await call(client, "run_shortcut", {"action": "run", "name": "X", "input": {"a": 1}})
        assert r.is_error is True
        assert "must be a string" in text(r)


async def test_check_permissions_reports_all_classes(session):
    async with session() as client:
        start = time.monotonic()
        r = await call(client, "check_permissions")
        elapsed_ms = (time.monotonic() - start) * 1000

        perms = parse_result(text(r))
        classes = ["accessibility", "automation", "screenRecording"]

        assert all(isinstance(perms[k].get("granted"), (bool, type(None))) for k in classes)
        assert all(isinstance(perms[k].get("unlocks"), list) and len(perms[k]["unlocks"]) > 0 for k in classes)

        # Probes are read-only; a prompt would block for seconds.
        assert elapsed_ms < 8000

        # A denied class must say where to grant it; a granted one need not.
        assert all(
            perms[k]["granted"] is True or (isinstance(perms[k].get("grantAt"), str) and "System Settings" in perms[k]["grantAt"])
            for k in classes
        )

        # Every tool name it mentions must actually exist.
        tools = await client.list_tools()
        listed = {t.name for t in tools.tools}
        mentioned = [n for k in classes for n in perms[k]["unlocks"]] + perms.get("noPermissionNeeded", [])
        assert all(n in listed for n in mentioned)
