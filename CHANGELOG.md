# Changelog

## 0.6.0 — 2026-11-26

- **React Native** (TypeScript/JavaScript, bare or Expo). The indexer reads function and class
  components, hooks, stores (Redux, Zustand, MobX) and contexts, with their props, state and
  handlers; `facts` shows what each component renders (from its JSX) and the hooks it calls.
  Module hints follow React Navigation's navigators or Expo Router's `app/` folder.
- **React Native screenshots** on Android and iOS: a dev-only helper inside the app measures each
  component the map draws from React's own tree and hands the rects to the native driver through
  a host relay; inactive tabs and screens under the top of a stack count as hidden.
  `app-map shots react-native android|ios <app> <map> <scenario> <out>`.
- A component's native file wins over its `.web` variant when names collide.
- **Seventh live example:** Bluesky (React Native and Expo, ~323k lines), with screenshots of its
  signed-out screens from the Android emulator.

## 0.5.0 — 2026-11-26

- **Homebrew:** `brew install yonivav/app-map/app-map`, then `app-map install --auto` in your app.
  `app-map install` takes the installer's options; every other command is the CLI.
- **Six live examples:** Flutter Gallery, Wikipedia for iOS and Wikipedia for Android join
  Wonderous, NetNewsWire and Now in Android, each with screenshots from a simulator or emulator.
- A 39-second demo video on the site.
- The pull-request bot commits only a map that passes its checks, whatever the agent's exit code;
  Gemini runs a Flash model by default (`GEMINI_MODEL` to change it).
- Leaner `SKILL.md` (the automation details load only when needed).
- `app-map changes --exit-code`: exits 1 when the map is behind the code.
- `app-map sync` remembers code that wasn't committed yet, so updating the map in the same change
  as the code no longer makes `changes` list that module again after the commit.
- `noCrop` in `app-map.json`: a crop that shows something wrong stays out on every run.
- New link-preview and LinkedIn images showing all three platforms.
- Kotlin `companion object` members are indexed: `Foo.create()` opens its code.
- The parse cache follows each language module's code, so an indexer fix reaches files parsed before.

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
