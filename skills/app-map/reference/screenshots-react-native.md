# Screenshots for a React Native app

A React Native app runs JavaScript inside a native shell, so neither the Flutter driver nor lldb
sees its components. Instead, a small dev-only helper inside the app (`appMapShots.js`) walks
React's own component tree and measures every component the map draws; the native driver takes
the screenshot and taps. Android today; iOS next.

Needs: Node, the Android SDK and a JDK the app builds with, the app building as a **debug**
build (Expo apps: a development build; Expo Go can't run it).

## 1. Write the scenario

Start from `adapters/react-native/example_scenario.kt`: a JUnit test on the app's `MainActivity`
that taps with UiAutomator — `By.text("…")`, `By.desc(accessibilityLabel)`, `By.res(testID)` —
and calls `shots.snap("module_nn_what")` on each screen. `openExpoDevBuild()` gets an Expo
development build past its launcher and first-run developer menu.

- The relay log (`<out>/relay.log`) lists, for each snap, every component name on screen
  (`SHOT SEEN …`): use it to name boxes and to find what to tap.
- Wait for network content before a snap, like on the other platforms.

## 2. Run it

```bash
<skill>/scripts/app-map shots react-native android <app dir> <map> <Scenario.kt> <out> [--minutes 20]
```

It copies the helper into the app and imports it first from the entry file (both restored when
the run ends), starts the relay and Metro, creates `android/` with `npx expo prebuild` if an
Expo app has none, then builds and runs the Android adapter with the test libraries a React
Native app lacks. Components inside an inactive tab or under the top of a stack are logged as
hidden, so `crop` never picks a covered copy.

## 3. Use the pictures

As for Flutter ([screenshots-flutter.md](screenshots-flutter.md) §3): pick 2–5 per module into
`<map>/shots/<module>/` (at the screen's dp size, e.g. 411 px wide), list them in the
frontmatter, then `scripts/app-map crop <out dir> <map>`. `Text` and other primitives have no
picture of their own; leave them out of the diagrams anyway.
