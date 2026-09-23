---
id: TASK-002
title: Fix Screen Recording permission handling for screenshot integration tests
status: Done
assignee: []
created_date: '2026-09-23 01:58'
updated_date: '2026-09-23 02:16'
labels: []
dependencies: []
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Three integration tests fail on dev machines where Screen Recording permission is denied to the terminal/app running the tests: test_screenshot_fullscreen, test_screenshot_window_mode_resolves_frontmost_app, test_screenshot_refuses_to_overwrite_by_default. screencapture's failure text ("could not create image from display/rect/window") doesn't match the tolerance substrings ("permission", "No windows found", "overwrite") those tests currently check for. This reproduces identically against the old Node server, so it's a pre-existing gap in the tolerance list, not a Python-port regression (see TASK-001.03/001.08 implementation notes). Fix by detecting the Screen Recording denial explicitly (e.g. via check_permissions' CGPreflightScreenCaptureAccess probe, or matching screencapture's actual failure strings) and returning/tolerating a message that identifies it as a permission problem.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 test_screenshot_fullscreen passes (or is correctly skipped) when Screen Recording permission is denied
- [x] #2 test_screenshot_window_mode_resolves_frontmost_app passes (or is correctly skipped) when Screen Recording permission is denied
- [x] #3 test_screenshot_refuses_to_overwrite_by_default passes (or is correctly skipped) when Screen Recording permission is denied
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added explicit Screen Recording denial detection for the screenshot tool: matches screencapture's known failure text ("could not create image from display/window/rect") and confirms via CGPreflightScreenCaptureAccess, returning a clear permission message instead of the raw osascript error. Verified against a real revoked-permission repro (tccutil reset ScreenCapture com.googlecode.iterm2) that all three affected integration tests now pass, then confirmed the full suite (unit + integration) is green with permission still denied.
<!-- SECTION:FINAL_SUMMARY:END -->
