# Changelog

## Unreleased

- Leaner `SKILL.md` (the automation details load only when needed).
- `app-map changes --exit-code`: exits 1 when the map is behind the code.
- `noCrop` in `app-map.json`: a crop that shows something wrong stays out on every run.
- New link-preview and LinkedIn images showing all three platforms.

## 0.4.0 — 2026-11-23

- **Native screenshots.** iOS: an XCUITest driver for any installed app (by bundle id), with
  lldb reading each view's class and frame, including app extensions and SwiftUI screens.
  Android: an instrumented test reading Activities, Fragments, Views and `@Composable` functions
  from Compose's inspector data; `--real-app` runs it under the app's own Application.
- **A picture for every page and widget:** `app-map crop` lists the ones still missing.
- **Automatic mode:** `install.sh --auto` makes your agent update the map with every code change,
  and adds pull-request workflows that update the map (Claude Code, Codex, Gemini CLI, Cursor or
  Copilot, picked with `--agent`) and check it.
- NetNewsWire and Now in Android maps get screenshots; the demo GIF ends on them.

## 0.3.0 — 2026-11-23

- **Native code maps:** Swift, Objective-C, Kotlin and Java, with classes, structs,
  protocols/interfaces, extensions/categories, SwiftUI views and `@Composable` functions.
- Example maps of NetNewsWire (iOS) and Now in Android, built and verified in CI.
- `exclude` in `app-map.json` leaves repo folders out (another platform's target).

## 0.2.0 — 2026-11-22

- First public release: Flutter apps mapped into Markdown UML pages and a clickable site, with
  code popups, screenshot crops, `changes`/`sync`/`where`, a CI check, and the Wonderous example.
- One install for every agent that reads Agent Skills (Claude Code, Cursor, Codex, Gemini CLI,
  Copilot).
