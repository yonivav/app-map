---
title: Home Menu Module
sub: 'The menu over Home: jump to any wonder, open the timeline or your collection, read About, or switch language.'
card_title: Home Menu
card: Wonder grid, timeline, collection, language
screenshots:
- file: shots/home-menu/01_menu.jpg
  caption: Wonder grid around the compass, links, 简体中文
---

## What it does {#what}

A blurred, half-transparent backdrop over Home holds a 3 × 3 grid: the 8 wonder buttons around a compass, each `shortestSide / 5` clamped to 60–100 px, the current wonder with a 5 px border. Tapping one pops the dialog with its `WonderType` and Home jumps there; tapping outside closes it. Below are three links that fade and slide in 50 ms apart after 250 ms: “Explore the timeline” (`/home/timeline?type=` the current wonder), “View your collection” (`/home/collection`) and “About this app”, a Material about dialog with the version, “© 2022 gskinner” and links that open in a full-screen web view on phones or the browser on desktop and web. The top-right button swaps English ↔ 简体中文: it saves `currentLocale`, reloads the strings, and re-runs `WondersLogic.init()` and `TimelineLogic.init()` because the wonder and event data hold translated text; `WondersApp` watches the locale and rebuilds.

## Logic · class diagram {#classes}

The menu is a dialog that returns a value: Home awaits the pushed route, and a language switch fans out through SettingsLogic to every logic class holding translated text.

```mermaid
classDiagram
  direction LR
  class HomeMenu {
    <<modal>>
    data
  }
  class _HomeMenuState {
    <<modal state>>
    _btnSize()
    _handleTimelinePressed()
    _handleCollectionPressed()
    _handleAboutPressed()
  }
  class _GridBtnState {
    <<widget state>>
    _handleWonderPressed()
  }
  class LocaleSwitcher { <<widget>> }
  class SettingsLogic {
    <<logic>>
    currentLocale
    changeLocale()
  }
  class LocaleLogic {
    <<logic>>
    strings
    loadIfChanged()
  }
  class WondersLogic {
    <<logic>>
    all
    init()
  }
  class TimelineLogic {
    <<logic>>
    init()
  }
  class ScreenPaths {
    <<data>>
    timeline() · collection()
  }
  class AboutDialogContent { <<widget>> }
  class FullscreenWebView { <<page>> }
  HomeMenu --> _HomeMenuState : createState
  _HomeMenuState ..> WondersLogic : all, 8 grid buttons
  _GridBtnState ..> HomeMenu : pops with WonderType
  _HomeMenuState ..> ScreenPaths : timeline() · collection()
  _HomeMenuState ..> AboutDialogContent : showAboutDialog
  AboutDialogContent ..> FullscreenWebView : links on mobile
  LocaleSwitcher ..> SettingsLogic : changeLocale()
  SettingsLogic ..> LocaleLogic : loadIfChanged()
  SettingsLogic ..> WondersLogic : init()
  SettingsLogic ..> TimelineLogic : init()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

Backdrop, an invisible tap-to-close underlay, then a centred column of the wonder grid and three text buttons, with the close and language buttons in the header.

```mermaid
classDiagram
  direction TB
  class HomeMenu { <<modal>> }
  class AppBackdrop {
    <<blur>>
    strength
  }
  class PopNavigatorUnderlay { <<tap to close>> }
  class _GridBtn { <<widget>> }
  class _MenuTextBtn {
    <<widget>>
    label · icon
  }
  class AppHeader { <<close button>> }
  class LocaleSwitcher { <<widget>> }
  class WonderData {
    <<data>>
    type · title
  }
  HomeMenu *-- AppBackdrop
  HomeMenu *-- PopNavigatorUnderlay
  HomeMenu *-- _GridBtn : 8, around a compass
  HomeMenu *-- _MenuTextBtn : timeline, collection, about
  HomeMenu *-- AppHeader
  AppHeader *-- LocaleSwitcher : trailing
  _GridBtn --> WonderData : btnData · selectedData
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Jump to a wonder, or switch language · sequence {#sequence}

The menu is awaited like a function call; the language switch never leaves the menu.

```mermaid
sequenceDiagram
  actor User
  participant Home as _HomeScreenState
  participant App as AppLogic
  participant Grid as _GridBtnState
  participant Switch as LocaleSwitcher
  participant Settings as SettingsLogic
  participant Locale as LocaleLogic
  participant Wonders as WondersLogic
  participant Timeline as TimelineLogic
  User->>Home: tap menu → _handleOpenMenuPressed()
  Home->>App: showFullscreenDialogRoute()
  App-->>User: HomeMenu fades in, 200 ms
  alt pick a wonder
    User->>Grid: tap → _handleWonderPressed()
    Grid-->>Home: route pops with the WonderType
    Home->>Home: _setPageIndex()
  else switch language
    User->>Switch: tap 简体中文
    Switch->>Settings: changeLocale()
    Settings->>Locale: loadIfChanged()
    Settings->>Wonders: init()
    Settings->>Timeline: init()
    Settings-->>User: WondersApp rebuilds in Chinese
  end
```

## Key files {#files}

- `lib/ui/screens/home_menu/home_menu.dart` · grid and menu links
- `lib/ui/screens/home_menu/about_dialog_content.dart` · About text and links
- `lib/ui/common/controls/locale_switcher.dart` · en ↔ zh button
- `lib/logic/settings_logic.dart` · changeLocale() fan-out
- `lib/ui/common/utils/page_routes.dart` · fade dialog route
