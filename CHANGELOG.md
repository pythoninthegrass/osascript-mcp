# Changelog

## [1.3.0](https://github.com/pythoninthegrass/osascript-mcp/compare/v1.2.0...v1.3.0) (2026-09-25)


### Features

* **executor:** support extra osascript args via OSASCRIPT_MCP_ARGS ([1304282](https://github.com/pythoninthegrass/osascript-mcp/commit/13042823374ae24fa6cc6f7301fce58a6ffafefb))


### Documentation

* move wall-of-text comments to docs/design-notes.md ([16bf1a6](https://github.com/pythoninthegrass/osascript-mcp/commit/16bf1a69cb9e206b3cf8edb9dbf47de382e1fc6d))

## [1.2.0](https://github.com/pythoninthegrass/osascript-mcp/compare/v1.1.3...v1.2.0) (2026-09-23)


### ⚠ BREAKING CHANGES

* measure TOON vs JSON output, default to minified JSON

### Features

* add release-please automation and act local-CI config ([bb4ce38](https://github.com/pythoninthegrass/osascript-mcp/commit/bb4ce38078d42c959ee9ac733406fedc28d2a4bf))
* measure TOON vs JSON output, default to minified JSON ([740722a](https://github.com/pythoninthegrass/osascript-mcp/commit/740722a47d4080f656b0da75983f2d71a4eae5f4))
* port executor.js to asyncio executor.py ([95857f5](https://github.com/pythoninthegrass/osascript-mcp/commit/95857f516994a61a6a7833093fd49184864b8c32))
* port server dispatch and all 18 tools to Python ([8952613](https://github.com/pythoninthegrass/osascript-mcp/commit/8952613ce1be184d544bbf74a94519b43086462b))
* support ordinal menu positions in app_menu ([7373a43](https://github.com/pythoninthegrass/osascript-mcp/commit/7373a43658202826f504982c9d9c779a1b57c450))


### Bug Fixes

* detect Screen Recording denial explicitly in screenshot tool ([6978dd8](https://github.com/pythoninthegrass/osascript-mcp/commit/6978dd8cbba51de1c988509dcc89d2f789a010b0))
* route digit keys through key code in press_key ([17df89d](https://github.com/pythoninthegrass/osascript-mcp/commit/17df89d2b716ca76f1ed68b1545ea7ed695753c2))


### Documentation

* **backlog:** add task for TOON output formatting option ([2e0e635](https://github.com/pythoninthegrass/osascript-mcp/commit/2e0e6351f9f1339ab315074de314e165291fb758))
* **backlog:** move TOON task under Node-&gt;Python conversion as TASK-001.13 ([dfc4964](https://github.com/pythoninthegrass/osascript-mcp/commit/dfc4964a58d89e399568a3c0022304db1a0b21a4))
* **backlog:** point TASK-002 at toon-format/toon, not the retiring npm package ([15ea60d](https://github.com/pythoninthegrass/osascript-mcp/commit/15ea60d7bb056debb82025fd4606cb3e0e9cc166))
* update README and AGENTS.md for the Python port ([7216deb](https://github.com/pythoninthegrass/osascript-mcp/commit/7216debcac903d118d7d4e32b6bd2b0c23aa161f))
