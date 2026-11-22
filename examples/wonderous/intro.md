---
title: Intro Module
sub: A three-page welcome at `/welcome`, shown until the user finishes it once.
card_title: Intro
card: Three-page welcome, shown once
screenshots:
- file: shots/intro/01_journey.jpg
  caption: Journey to the past
- file: shots/intro/02_explore_places.jpg
  caption: Explore places
- file: shots/intro/03_discover_artifacts.jpg
  caption: Discover artifacts, then the arrow
---

## What it does {#what}

Three pages — “Journey to the past”, “Explore places”, “Discover artifacts” — each pair a title and a line of text with a photo (camel, Petra, statue) cut out by its own mask image. Only the text actually swipes: a full-screen `PageView` carries the titles, and the logo, the 250 px image (150 px when the screen is under 550 px tall) and the page dots sit in a fixed layer on top, lined up with gaps in each page. The image cross-fades in 900 ms when the page changes, each swipe gives a light haptic tap, and the whole screen fades in after 500 ms. On the last page the “Swipe left to continue” hint fades out and an orange finish button fades in (300 ms); pressing it sets `hasCompletedOnboarding` (saved to `settings.dat`) and goes to `/home` inside `Router.neglect`, so `/welcome` never comes back — the router also redirects it to home from then on. On desktop and web, `PreviousNextNavigation` adds arrow buttons and arrow-key paging (max width 600).

## Logic · class diagram {#classes}

All state is local to the screen: a PageController drives a page-index notifier, and the only thing that leaves the screen is the onboarding flag.

```mermaid
classDiagram
  direction LR
  class IntroScreen { <<page>> }
  class _IntroScreenState {
    <<page state>>
    _pageController · _currentPage
    pageData
    _handlePageChanged()
    _incrementPage()
    _handleIntroCompletePressed()
  }
  class _PageData {
    <<data>>
    title · desc · img · mask
  }
  class SettingsLogic {
    <<logic>>
    hasCompletedOnboarding
  }
  class ScreenPaths {
    <<data>>
    home
  }
  class AppHaptics {
    <<data>>
    lightImpact()
  }
  IntroScreen --> _IntroScreenState : createState
  _IntroScreenState o-- _PageData : pageData, 3 pages
  _IntroScreenState ..> SettingsLogic : sets hasCompletedOnboarding
  _IntroScreenState ..> ScreenPaths : go home
  _IntroScreenState ..> AppHaptics : lightImpact()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

Two layers in one Stack: a swipeable PageView of text pages, and a fixed column of logo, masked image and dots that ignores touches.

```mermaid
classDiagram
  direction TB
  class IntroScreen { <<page>> }
  class PreviousNextNavigation { <<desktop arrows>> }
  class PageView { <<swipes the text>> }
  class _Page { <<widget>> }
  class IgnorePointerKeepSemantics { <<fixed layer>> }
  class _WonderousLogo { <<widget>> }
  class _PageImage { <<widget>> }
  class AppPageIndicator {
    <<widget>>
    count · controller
  }
  class HzGradient { <<edge fade>> }
  class CircleIconBtn { <<finish button>> }
  class _PageData { <<data>> }
  IntroScreen *-- PreviousNextNavigation
  PreviousNextNavigation *-- PageView
  PageView *-- _Page : x3
  PreviousNextNavigation *-- IgnorePointerKeepSemantics
  IgnorePointerKeepSemantics *-- _WonderousLogo
  IgnorePointerKeepSemantics *-- _PageImage : AnimatedSwitcher
  IgnorePointerKeepSemantics *-- AppPageIndicator
  PreviousNextNavigation *-- HzGradient : x2
  PreviousNextNavigation *-- CircleIconBtn : mobile, last page
  _Page --> _PageData
  _PageImage --> _PageData
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Swipe through and enter the app · sequence {#sequence}

Paging only moves the text; the fixed layer listens to the page index and swaps the image.

```mermaid
sequenceDiagram
  actor User
  participant Pages as PageView
  participant Intro as _IntroScreenState
  participant Image as _PageImage
  participant Settings as SettingsLogic
  participant Router as GoRouter
  User->>Pages: swipe left
  Pages->>Intro: _handlePageChanged()
  Intro->>Intro: _currentPage = page index
  Intro->>Intro: AppHaptics light impact
  Intro->>Image: AnimatedSwitcher cross-fades the next photo, 900 ms
  User->>Pages: swipe to page 3
  Intro->>Intro: finish button fades in, hint fades out
  User->>Intro: tap finish → _handleIntroCompletePressed()
  Intro->>Settings: hasCompletedOnboarding = true
  Settings->>Settings: scheduleSave(), at most every 2 s
  Intro->>Router: go /home inside Router.neglect
  Router-->>User: Home, and /welcome now redirects there
```

## Key files {#files}

- `lib/ui/screens/intro/intro_screen.dart` · pages, logo, masked image
- `lib/ui/common/previous_next_navigation.dart` · desktop arrows and keys
- `lib/ui/common/controls/app_page_indicator.dart` · page dots
- `lib/logic/settings_logic.dart` · hasCompletedOnboarding flag
