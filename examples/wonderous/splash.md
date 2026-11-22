---
title: Splash Module
sub: 'The app boots behind the native splash: get_it registers the logic layer, `AppLogic.bootstrap()` loads saved state, and GoRouter swaps the hidden `/` route for the intro or home.'
card_title: Splash
card: Boot, get_it singletons, GoRouter redirects
screenshots:
- file: shots/splash/01_native_splash.jpg
  caption: Native launch screen while bootstrap runs
---

## What it does {#what}

`main()` keeps the native splash on screen (`FlutterNativeSplash.preserve`), registers 10 lazy singletons with get_it (8 logic classes plus `ArtifactAPIService` and `NativeWidgetService`) and starts `WondersApp`, a `MaterialApp.router` on the global `appRouter` whose locale follows `SettingsLogic.currentLocale`. Views reach logic through 8 top-level getters (`appLogic`, `wondersLogic`, `settingsLogic`…); services deliberately get no shortcut. `bootstrap()` then sets a 380×650 minimum window on desktop, loads the map-marker bitmap, asks Android for its highest refresh rate, loads settings and strings, builds the 8 wonders, the timeline events and the collectibles, waits 1 ms so GoRouter can catch a deep link, flips `isBootstrapComplete` and goes to `/welcome` on first run, otherwise to the saved deep link or `/home` (inside `Router.neglect`, so `/` never becomes a back target). Until then `_handleRedirect` sends every path to `/` and remembers the first as the deep link; afterwards it sends `/`, and `/welcome` once onboarding is done, to `/home`. Settings and collectibles are JSON strings in SharedPreferences (`settings.dat`, `collectibles.dat`), saved at most once every 2 s by `Throttler`. Every screen is an `AppRoute`: a Cupertino page (swipe back) or a fade when `useFade` is set or animations are off, and `ScreenPaths` appends nested pages (video, search, maps, timeline, artifact, collection) to the current path so back returns where you came from.

## Logic · class diagram {#classes}

One composition root: get_it owns every logic singleton, AppLogic runs them in order at boot, and the router reads two of their flags to decide where the app may go.

```mermaid
classDiagram
  direction LR
  class registerSingletons { <<function>> }
  class GetIt { <<service locator>> }
  class WondersApp { <<app>> }
  class appRouter { <<GoRouter>> }
  class _handleRedirect { <<redirect>> }
  class AppRoute {
    <<route>>
    useFade
  }
  class ScreenPaths {
    <<data>>
    splash · intro · home
    wonderDetails()
    video() · search() · maps()
    timeline() · artifact() · collection()
    _appendToCurrentPath()
  }
  class AppLogic {
    <<logic>>
    isBootstrapComplete
    bootstrap()
    handleAppSizeChanged()
    shouldUseNavRail()
    showFullscreenDialogRoute()
  }
  class SettingsLogic {
    <<logic>>
    hasCompletedOnboarding
    currentLocale · prevWonderIndex
    isSearchPanelOpen · hasDismissedSearchMessage
    changeLocale()
  }
  class LocaleLogic {
    <<logic>>
    strings
    load()
  }
  class WondersLogic {
    <<logic>>
    all
    init()
  }
  class TimelineLogic {
    <<logic>>
    events
    init()
  }
  class CollectiblesLogic {
    <<logic>>
    statesById
    init()
  }
  class ThrottledSaveLoadMixin {
    <<mixin>>
    fileName
    load() · save()
    scheduleSave()
  }
  class JsonPrefsFile {
    <<storage>>
    load() · save()
  }
  class Throttler {
    <<data>>
    interval
    call()
  }
  registerSingletons ..> GetIt : registers 10 lazy singletons
  GetIt o-- AppLogic : appLogic
  GetIt o-- SettingsLogic : settingsLogic
  GetIt o-- LocaleLogic : localeLogic
  GetIt o-- WondersLogic : wondersLogic
  GetIt o-- TimelineLogic : timelineLogic
  GetIt o-- CollectiblesLogic : collectiblesLogic
  WondersApp ..> appRouter : routerDelegate
  WondersApp ..> SettingsLogic : watches currentLocale
  appRouter o-- AppRoute : routes
  appRouter --> _handleRedirect : redirect
  AppRoute ..> ScreenPaths : paths
  _handleRedirect ..> AppLogic : isBootstrapComplete
  _handleRedirect ..> SettingsLogic : hasCompletedOnboarding
  AppLogic ..> SettingsLogic : load()
  AppLogic ..> LocaleLogic : load()
  AppLogic ..> WondersLogic : init()
  AppLogic ..> TimelineLogic : init()
  AppLogic ..> CollectiblesLogic : init() · load()
  AppLogic ..> appRouter : go intro or home
  ThrottledSaveLoadMixin <|-- SettingsLogic
  ThrottledSaveLoadMixin <|-- CollectiblesLogic
  ThrottledSaveLoadMixin --> JsonPrefsFile : _file
  ThrottledSaveLoadMixin --> Throttler : _throttle
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

A ShellRoute wraps every screen in WondersAppScaffold, which rebuilds the shared AppStyle from the screen size; each route then picks a swipe-back or a fade page.

```mermaid
classDiagram
  direction TB
  class WondersApp { <<app>> }
  class MaterialApp { <<router app>> }
  class WondersAppScaffold {
    <<shell route>>
    style
  }
  class AppStyle {
    <<model>>
    scale · disableAnimations · highContrast
    colors · insets · text · times · sizes
  }
  class AppScrollBehavior { <<scroll behavior>> }
  class AppRoute {
    <<route>>
    useFade
  }
  class CupertinoPage { <<swipe-back page>> }
  class CustomTransitionPage { <<fade page>> }
  class PageNotFound { <<page>> }
  WondersApp *-- MaterialApp
  MaterialApp *-- WondersAppScaffold : ShellRoute
  MaterialApp *-- PageNotFound : unknown path
  WondersAppScaffold --> AppStyle
  WondersAppScaffold *-- AppScrollBehavior
  WondersAppScaffold *-- AppRoute : each screen
  AppRoute ..> CupertinoPage : builds
  AppRoute ..> CustomTransitionPage : builds
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Launch the app · sequence {#sequence}

Cold start: the native splash stays up until bootstrap finishes, then the router replaces the empty / route.

```mermaid
sequenceDiagram
  actor User
  participant Main as main
  participant GetIt
  participant Router as appRouter
  participant Redirect as _handleRedirect
  participant App as AppLogic
  participant Settings as SettingsLogic
  participant Locale as LocaleLogic
  participant Wonders as WondersLogic
  participant Collect as CollectiblesLogic
  User->>Main: cold launch
  Main->>Main: keep native splash up
  Main->>GetIt: registerSingletons, 10 lazy singletons
  Main->>Router: runApp WondersApp on appRouter
  Router->>Redirect: initial location /
  Redirect-->>Router: stay on /, remember any deep link
  Main->>App: bootstrap()
  App->>Settings: load()
  App->>Locale: load()
  App->>Wonders: init()
  App->>Collect: load()
  Note over App: waits 1 ms so GoRouter catches the initial deep link
  App->>Router: go /welcome on first run, else deep link or /home
  Router->>Redirect: isBootstrapComplete is now true
  Main->>User: remove native splash
```

## Key files {#files}

- `lib/main.dart` · get_it registration, WondersApp
- `lib/router.dart` · ScreenPaths, routes, redirect
- `lib/logic/app_logic.dart` · bootstrap and orientation
- `lib/logic/settings_logic.dart` · five saved settings
- `lib/logic/locale_logic.dart` · loads en / zh strings
- `lib/logic/common/save_load_mixin.dart` · throttled JSON persistence
- `lib/logic/common/json_prefs_file.dart` · SharedPreferences JSON file
- `lib/ui/app_scaffold.dart` · shell, AppStyle per size
- `lib/styles/styles.dart` · AppStyle tokens and timings
