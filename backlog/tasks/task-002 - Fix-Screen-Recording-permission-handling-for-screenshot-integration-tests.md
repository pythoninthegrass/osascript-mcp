---
id: TASK-002
title: Fix Screen Recording permission handling for screenshot integration tests
status: To Do
assignee: []
created_date: '2026-09-23 01:58'
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
- [ ] #1 test_screenshot_fullscreen passes (or is correctly skipped) when Screen Recording permission is denied
- [ ] #2 test_screenshot_window_mode_resolves_frontmost_app passes (or is correctly skipped) when Screen Recording permission is denied
- [ ] #3 test_screenshot_refuses_to_overwrite_by_default passes (or is correctly skipped) when Screen Recording permission is denied
<!-- AC:END -->
