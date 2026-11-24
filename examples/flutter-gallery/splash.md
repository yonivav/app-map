---
title: Splash Module
sub: A full-screen Flutter logo over one of ten animated effects, hidden behind the home page until you pull it down.
card_title: Splash
card: Ten random logo effects behind the home page
screenshots:
- file: shots/splash/01_effect.jpg
  caption: 'Pulled down: one of ten random effects, home peeking at the bottom'
---

## What it does {#what}

On a phone the splash is a back layer: the home page normally covers it completely. Flinging the top 40 pt of the home page downward (faster than 200 px/s) sends a `ToggleSplashNotification`, and the home page slides down over 300 ms (`easeInOut`) until only 60 pt of it peeks at the bottom. Behind it plays one of ten looping GIFs, picked at random when the page is created (`splash_effect_1.gif` to `splash_effect_10.gif`, on a `#030303` background), with the Flutter logo centred on top. Tapping the peeking home page, or flinging it up faster than 200 px/s, slides it back. On desktop the home page stays 210 pt down with rounded 40 pt top corners and a clickable logo above it; on a foldable the two layers sit side by side in a `TwoPane`. `SplashPageAnimation` tells the home page whether the splash has finished, so its entrance animation starts only once.

## Logic · class diagram {#classes}

One animation controller moves the front layer; the back layer only decides which picture to show.

```mermaid
classDiagram
  direction LR
  class RootPage { <<page>> }
  class SplashPage {
    <<page>>
    child
  }
  class _SplashPageState {
    <<page state>>
    _controller · _effect
    _isSplashVisible
    _getPanelAnimation()
  }
  class SplashPageAnimation {
    <<inherited>>
    isFinished
    of()
  }
  class _SplashBackLayer {
    <<widget>>
    isSplashCollapsed · effect
    onTap
  }
  class ToggleSplashNotification { <<notification>> }
  class Backdrop { <<front layer>> }
  RootPage *-- SplashPage
  SplashPage --> _SplashPageState : createState
  _SplashPageState --> SplashPageAnimation : provides isFinished
  _SplashPageState *-- _SplashBackLayer : back layer
  _SplashPageState *-- Backdrop : front layer, slides
  ToggleSplashNotification ..> _SplashPageState : opens the splash
```

- `──▷` holds
- `◆──` contains
- `┄┄▷` uses

## Pull down the splash · sequence {#sequence}

The home page never calls the splash directly: it bubbles a notification up the tree.

```mermaid
sequenceDiagram
  actor User
  participant Home as _AnimatedHomePage
  participant Notif as ToggleSplashNotification
  participant Splash as _SplashPageState
  participant Back as _SplashBackLayer
  User->>Home: fling the top 40 pt down, faster than 200 px/s
  Home->>Notif: dispatches it
  Notif->>Splash: NotificationListener catches it
  Splash->>Splash: controller runs forward, 300 ms
  Splash->>Back: isSplashCollapsed = false
  Back-->>User: random GIF and the Flutter logo, home peeks 60 pt
  User->>Splash: tap the peeking home page
  Splash->>Splash: controller runs in reverse
  Splash-->>User: home page slides back up
```

## Key files {#files}

- `lib/pages/splash.dart` · splash layers and animation
- `lib/main.dart` · `RootPage`: splash around the backdrop
- `lib/constants.dart` · animation durations
