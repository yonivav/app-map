---
title: Home Module
sub: A looping, parallax carousel of the eight wonders; swipe sideways to browse, swipe up to step into one.
card_title: Home
card: Parallax carousel of the eight wonders
screenshots:
- file: shots/home/01_carousel.jpg
  caption: The Great Wall in the looping carousel
- file: shots/home/02_petra.jpg
  caption: 'Swiped to Petra: new colors and illustration'
---

## What it does {#what}

Each wonder is drawn in three layers — a background (sky colour, texture, sun or moon), a middle illustration in a `PageView`, and foreground pieces at the edges — plus clouds seeded per wonder that drift in over 1.5 s. The carousel starts at page 8 × 100 + the last wonder viewed (saved as `prevWonderIndex`), so it loops both ways; changing wonder gives a light haptic and each layer animates its pieces in or out over 450 ms. Pulling up 150 px opens the wonder: while you drag, every piece scales by its own `zoomAmt` × the pull (× 0.4 for the foreground, × 0.05 for the middle) and the bottom gradient darkens; letting go early springs back over half a second per full pull. Opening goes to `/home/wonder/?t=0` with a fade while the foreground is frozen in place, and on return the foreground fades back in after 300 ms. The arrow button and a trackpad scroll up open it too; the 8 px page dots and desktop arrow keys jump between wonders. The menu button opens `HomeMenu` as a 200 ms fade dialog and jumps to whichever wonder is picked there.

## Logic · class diagram {#classes}

The screen state owns an infinite PageController and a small swipe controller; both just feed numbers into the shared illustration widgets.

```mermaid
classDiagram
  direction LR
  class HomeScreen { <<page>> }
  class _HomeScreenState {
    <<page state>>
    _wonderIndex · _isMenuOpen
    _swipeOverride · _fadeInOnNextBuild
    _handlePageChanged()
    _setPageIndex()
    _handleOpenMenuPressed()
    _showDetailsPage()
    _startDelayedFgFade()
  }
  class _VerticalSwipeController {
    <<controller>>
    swipeAmt · isPointerDown
    handleVerticalSwipeUpdate()
    handleVerticalSwipeCancelled()
    buildListener()
    wrapGestureDetector()
  }
  class PageController { <<infinite carousel>> }
  class WondersLogic {
    <<logic>>
    all
  }
  class WonderData {
    <<data>>
    type · title
  }
  class SettingsLogic {
    <<logic>>
    prevWonderIndex
  }
  class AppLogic {
    <<logic>>
    showFullscreenDialogRoute()
  }
  class HomeMenu { <<modal>> }
  class ScreenPaths {
    <<data>>
    wonderDetails()
  }
  class WonderIllustrationConfig {
    <<model>>
    zoom · isShowing
    fg() · mg() · bg()
  }
  HomeScreen --> _HomeScreenState : createState
  _HomeScreenState --> PageController : _pageController
  _HomeScreenState --> _VerticalSwipeController : _swipeController
  _VerticalSwipeController ..> _HomeScreenState : onSwipeComplete
  _HomeScreenState ..> WondersLogic : all
  WondersLogic o-- WonderData : all
  _HomeScreenState ..> SettingsLogic : prevWonderIndex
  _HomeScreenState ..> AppLogic : showFullscreenDialogRoute()
  AppLogic ..> HomeMenu : returns picked WonderType
  _HomeScreenState ..> ScreenPaths : wonderDetails()
  _HomeScreenState ..> WonderIllustrationConfig : bg() · mg() · fg()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

A Stack of four layers — 8 backgrounds, the middle PageView, 8 foregrounds, floating UI — where only the selected wonder’s layers are showing.

```mermaid
classDiagram
  direction TB
  class HomeScreen { <<page>> }
  class WonderIllustration {
    <<widget>>
    type · config
  }
  class AnimatedClouds {
    <<widget>>
    wonderType · opacity
  }
  class PageView { <<middle layer>> }
  class WonderTitleText {
    <<widget>>
    enableShadows · enableHero
  }
  class AppPageIndicator {
    <<widget>>
    count · dotSize
  }
  class _AnimatedArrowButton { <<widget>> }
  class AppHeader { <<menu button>> }
  class PetraIllustration { <<one per wonder>> }
  class WonderIllustrationBuilder {
    <<widget>>
    bgBuilder · mgBuilder · fgBuilder
  }
  class IllustrationPiece {
    <<widget>>
    fileName · heightFactor
    zoomAmt · initialOffset · enableHero
  }
  class WonderIllustrationConfig { <<model>> }
  HomeScreen *-- WonderIllustration : 8 backgrounds + 8 foregrounds
  HomeScreen *-- AnimatedClouds
  HomeScreen *-- PageView
  PageView *-- WonderIllustration : middle layer
  HomeScreen *-- WonderTitleText
  HomeScreen *-- AppPageIndicator
  HomeScreen *-- _AnimatedArrowButton
  HomeScreen *-- AppHeader
  WonderIllustration --> WonderIllustrationConfig
  WonderIllustration *-- PetraIllustration
  PetraIllustration *-- WonderIllustrationBuilder
  WonderIllustrationBuilder *-- IllustrationPiece
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Pick a wonder and swipe up into it · sequence {#sequence}

Sideways paging is a plain PageView; the upward pull is a hand-rolled gesture that ends in a route change.

```mermaid
sequenceDiagram
  actor User
  participant Pages as PageView
  participant Home as _HomeScreenState
  participant Settings as SettingsLogic
  participant Swipe as _VerticalSwipeController
  participant Paths as ScreenPaths
  participant Router as GoRouter
  User->>Pages: swipe sideways
  Pages->>Home: _handlePageChanged()
  Home->>Settings: prevWonderIndex = page % 8
  Home->>Home: haptic, layers swap isShowing
  User->>Swipe: drag up → handleVerticalSwipeUpdate()
  Swipe->>Swipe: swipeAmt += drag / 150 px, 0 to 1
  Swipe-->>Home: buildListener() rebuilds zoom and gradients
  Note over Swipe: let go before 1 → handleVerticalSwipeCancelled() springs back
  Swipe->>Home: swipeAmt hits 1 → _showDetailsPage()
  Home->>Paths: wonderDetails()
  Home->>Router: go /home/wonder/type?t=0, fade
  Home->>Home: freeze foreground, 100 ms
  User->>Router: back to /home
  Home->>Home: _startDelayedFgFade(), after 300 ms
```

## Key files {#files}

- `lib/ui/screens/home/wonders_home_screen.dart` · carousel and layer stack
- `lib/ui/screens/home/_vertical_swipe_controller.dart` · swipe-up gesture
- `lib/ui/wonder_illustrations/` · eight layered illustrations
- `lib/ui/wonder_illustrations/common/wonder_illustration_builder.dart` · bg/mg/fg layer animation
- `lib/ui/wonder_illustrations/common/illustration_piece.dart` · one positioned image piece
- `lib/ui/wonder_illustrations/common/animated_clouds.dart` · seeded drifting clouds
- `lib/logic/wonders_logic.dart` · the 8 WonderData
- `lib/logic/data/wonders_data/` · per-wonder text and numbers
