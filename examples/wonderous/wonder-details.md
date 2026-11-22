---
title: Wonder Details Module
sub: The four-tab shell for one wonder at `/home/wonder/?t=`; the tab lives in the URL.
card_title: Wonder Details
card: Four-tab shell, tab kept in the URL
screenshots:
- file: shots/wonder-details/01_tabs.jpg
  caption: Machu Picchu, tab 0, with the tab bar
---

## What it does {#what}

The route fades in and hosts four full-screen tabs: “information and history” ([Editorial](editorial.html)), “photo gallery”, “artifacts” and “events”. The tab index comes from `?t=`, clamped to 0–3, and tapping a tab writes it back with `context.go`, so back, deep links and the web URL all land on the right tab. `LazyIndexedStack` builds a tab the first time it is shown and keeps it alive afterwards, so each tab keeps its scroll position. The bar has a 74 px round wonder button that returns home and four icon buttons sized (available length − 74 − 24) / 4, clamped to 25–100 px. Its white background fades out on the photo tab, where the icons turn white. When the window is wider than tall (and taller than 250 px) the bar becomes a vertical rail on the left. The bar measures itself and passes its size minus a 12 px inset to the tabs as `contentPadding`, so their content stops above it.

## Logic · class diagram {#classes}

The shell keeps a TabController and the URL in step, and decides between a bottom bar and a side rail from the window shape.

```mermaid
classDiagram
  direction LR
  class WonderDetailsScreen {
    <<page>>
    type · tabIndex
  }
  class _WonderDetailsScreenState {
    <<page state>>
    _tabController · _tabBarSize · _useNavRail
    _handleTabTapped()
    _handleTabChanged()
    _handleTabMenuSized()
    _clampIndex()
  }
  class TabController { <<4 tabs>> }
  class WondersLogic {
    <<logic>>
    getData()
  }
  class WonderData {
    <<data>>
    type · unsplashCollectionId
  }
  class AppLogic {
    <<logic>>
    shouldUseNavRail()
  }
  class ScreenPaths {
    <<data>>
    wonderDetails()
    home
  }
  class WonderType { <<enum>> }
  WonderDetailsScreen --> _WonderDetailsScreenState : createState
  WonderDetailsScreen --> WonderType : type
  _WonderDetailsScreenState --> TabController : _tabController
  _WonderDetailsScreenState ..> WondersLogic : getData()
  WondersLogic o-- WonderData : all
  _WonderDetailsScreenState ..> AppLogic : shouldUseNavRail()
  _WonderDetailsScreenState ..> ScreenPaths : wonderDetails()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

A Stack: the four tab screens in a lazy IndexedStack, with the measured tab menu aligned to the bottom or the left.

```mermaid
classDiagram
  direction TB
  class WonderDetailsScreen { <<page>> }
  class LazyIndexedStack {
    <<widget>>
    index
  }
  class WonderEditorialScreen { <<tab 0>> }
  class PhotoGallery { <<tab 1>> }
  class ArtifactCarouselScreen { <<tab 2>> }
  class WonderEvents { <<tab 3>> }
  class MeasurableWidget {
    <<widget>>
    onChange
  }
  class WonderDetailsTabMenu {
    <<widget>>
    showBg · axis
    buttonInset · homeBtnSize
    minTabSize · maxTabSize
  }
  class _WonderHomeBtn { <<widget>> }
  class _TabBtn {
    <<widget>>
    index · iconImg · label
  }
  WonderDetailsScreen *-- LazyIndexedStack
  LazyIndexedStack *-- WonderEditorialScreen
  LazyIndexedStack *-- PhotoGallery
  LazyIndexedStack *-- ArtifactCarouselScreen
  LazyIndexedStack *-- WonderEvents
  WonderDetailsScreen *-- MeasurableWidget
  MeasurableWidget *-- WonderDetailsTabMenu
  WonderDetailsTabMenu *-- _WonderHomeBtn
  WonderDetailsTabMenu *-- _TabBtn : x4
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Open a wonder and switch tabs · sequence {#sequence}

The URL is the source of truth for the tab; the stack only builds what has been visited.

```mermaid
sequenceDiagram
  actor User
  participant Router as GoRouter
  participant Shell as _WonderDetailsScreenState
  participant Wonders as WondersLogic
  participant App as AppLogic
  participant Menu as _TabBtn
  participant Tabs as TabController
  participant Stack as LazyIndexedStack
  Router->>Shell: WonderDetailsScreen type, tabIndex 0
  Shell->>Wonders: getData()
  Shell->>App: shouldUseNavRail()
  Shell->>Stack: index 0, builds the editorial only
  User->>Menu: tap artifacts icon
  Menu->>Shell: _handleTabTapped()
  Shell->>Tabs: index = 2
  Tabs-->>Shell: _handleTabChanged(), setState
  Shell->>Router: go /home/wonder/type?t=2
  Router->>Shell: didUpdateWidget(), same tab, nothing to do
  Shell->>Stack: index 2, builds ArtifactCarouselScreen once
  Note over Stack: tabs already built stay alive with their scroll position
```

## Key files {#files}

- `lib/ui/screens/wonder_details/wonders_details_screen.dart` · tab host, URL sync
- `lib/ui/screens/wonder_details/wonder_details_tab_menu.dart` · bar or rail, buttons
- `lib/ui/common/lazy_indexed_stack.dart` · build on first visit
- `lib/ui/common/measurable_widget.dart` · reports the bar size
- `lib/router.dart` · wonder route and sub-routes
