# Screenshots for a native Android app

An instrumented test taps through the app on an emulator of its own ("app-map_Pixel") and
takes each module's screenshots. At every snap it logs where each class of the map sits on
screen: Activities, Fragments and Views by class name, and `@Composable` functions by name,
from Compose's own inspector data (what Android Studio's Layout Inspector reads). `app-map crop`
then cuts one picture per class for the popups.

Needs: the Android SDK with an emulator system image, a JDK (Android Studio's is found), and
the app's module building with Gradle. For Compose, a debug build with `ui-tooling` (most apps
have `debugImplementation("androidx.compose.ui:ui-tooling")`; add it if missing).

## 1. Write the scenario

Start from `adapters/android/example_scenario.kt`: a JUnit test in package `appmap` that
launches the app's activity with `createAndroidComposeRule` (or `ActivityScenarioRule`), and
calls `AppMapShots.enable()` in `init`, before the activity starts. One step per screen:

```kotlin
shots.step("bookmarks") {
    compose.onNodeWithText("Saved").performClick()
    settle()
    shots.snap("bookmarks_01_saved")   // screenshot + every class of the map on screen
}
```

| Helper | Does |
|---|---|
| `AppMapShots(listOf(…))` | the classes the map draws; names never on screen are simply not found |
| `step("name") { … }` | runs a step; a failure is logged and the run goes on |
| `snap("module_nn_what")` | screenshot + `SHOT RECT` lines (dp) for every class of the map on screen |
| `report()` | the last line of the test |

Navigate with the app's own test tools: Compose test (`onNodeWithText`, `onNodeWithTag`,
`performClick`, `performTextInput`), Espresso (`pressBack`, `closeSoftKeyboard`).

- A Hilt app needs `@HiltAndroidTest`, `HiltAndroidRule` (order 0) and `hiltRule.inject()`,
  like its other instrumented tests; its test modules then supply the data.
- Images loaded from the network may not arrive in time: wait for them (`Thread.sleep`) before
  the snap, and drop a crop that still shows a placeholder.

## 2. Run it

```bash
<skill>/scripts/app-map shots android <app module dir> <Scenario.kt> <out dir> [--variant DemoDebug]
```

It copies `AppMapShots.kt` and the scenario into the module's `src/androidTest/kotlin/appmap/`
(listed in `.git/info/exclude`, never committed), starts the emulator (creating it on first
use), builds and installs the app and its test APK, runs the scenario with `am instrument`
(not Gradle's task, which uninstalls the app and its screenshots) and copies the screenshots
and `drive.log` to `<out dir>`. `instrument.log` has the test's own output.

## 3. Use the pictures

As for Flutter ([screenshots-flutter.md](screenshots-flutter.md) §3): pick 2–5 per module into
`<map>/shots/<module>/` (at the screen's dp size, e.g. 411 px wide), list them in the
frontmatter, then `scripts/app-map crop <out dir> <map>` and look through every crop.
