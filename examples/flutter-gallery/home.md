---
title: Home Module
sub: A carousel of six full app studies, then the Material, Cupertino and Reference demo lists that expand in place.
card_title: Home
card: Studies carousel and three demo categories
screenshots:
- file: shots/home/01_top.jpg
  caption: The Gallery header, the studies carousel and three categories
- file: shots/home/02_material.jpg
  caption: MATERIAL expanded in place
- file: shots/home/03_list.jpg
  caption: Each demo row opens /demo/<slug>
---

## What it does {#what}

The phone layout is one `ListView`: a **Gallery** header, a carousel of six study cards (Reply, Shrine, Rally, Crane, Fortnightly, Starter app), a **Categories** header and three expandable lists — Material (24 demos), Cupertino (13) and Reference (5). The carousel is a `PageView` sized so each 296 pt card plus its margins fills one page; cards shrink by 30 % per page of distance from the centre, eased out. 150 ms into launch the page plays an 800 ms entrance: the carousel slides in, the second card animates separately, and the three categories follow 0.00, 0.05 and 0.10 of the way through. Each card shows its light or dark artwork and colours, and tapping it pops to `/` and pushes the study's route. Tapping a category header expands its list over 200 ms; which lists are open, and the carousel page, are saved with state restoration. Tapping a demo pushes `/demo/<slug>`. On desktop the same content becomes a snapping horizontal carousel with arrow buttons and three side-by-side category columns, plus the About, Feedback and attribution links.

## Logic · class diagram {#classes}

`HomePage` is stateless: it builds the six cards from the studies registry and hands them to the animated mobile page.

```mermaid
classDiagram
  direction LR
  class HomePage {
    <<page>>
    build()
  }
  class _AnimatedHomePage { <<page>> }
  class _AnimatedHomePageState {
    <<page state>>
    _animationController · _launchTimer
    _isMaterialListExpanded
    _isCupertinoListExpanded
    _isOtherListExpanded
  }
  class Demos {
    <<registry>>
    studies()
    materialDemos()
    cupertinoDemos()
    otherDemos()
  }
  class GalleryDemo {
    <<data>>
    title · subtitle · slug
    category · configurations
  }
  class GalleryDemoCategory {
    <<enum>>
    study · material · cupertino · other
  }
  class SplashPageAnimation {
    <<inherited>>
    isFinished
  }
  class GalleryOptions {
    <<data>>
    isTestMode
  }
  class StudyWrapper {
    <<widget>>
    study · hasBottomNavBar
  }
  HomePage ..> Demos : studies()
  HomePage --> _AnimatedHomePage : carouselCards
  HomePage ..> SplashPageAnimation : isFinished
  _AnimatedHomePage --> _AnimatedHomePageState : createState
  _AnimatedHomePageState ..> Demos : materialDemos() · cupertinoDemos() · otherDemos()
  _AnimatedHomePageState ..> GalleryOptions : isTestMode opens every list
  Demos o-- GalleryDemo
  GalleryDemo --> GalleryDemoCategory : category
  HomePage ..> StudyWrapper : a card's route opens a study inside it
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · widget composition {#widgets}

Everything below the headers is wrapped in an entrance animation driven by one controller.

```mermaid
classDiagram
  direction TB
  class _AnimatedHomePage { <<page>> }
  class Header {
    <<widget>>
    color · text
  }
  class _MobileCarousel {
    <<widget>>
    animationController · children
  }
  class _AnimatedCarousel { <<entrance>> }
  class _AnimatedCarouselCard { <<entrance, card 2>> }
  class _CarouselCard {
    <<widget>>
    demo · asset · assetDark
    studyRoute
  }
  class _AnimatedCategoryItem {
    <<entrance>>
    topPaddingAnimation
  }
  class CategoryListItem {
    <<widget>>
    category · demos
    initiallyExpanded
  }
  class CategoryDemoItem {
    <<widget>>
    demo
  }
  _AnimatedHomePage *-- Header : Gallery and Categories
  _AnimatedHomePage *-- _MobileCarousel
  _MobileCarousel *-- _AnimatedCarousel
  _MobileCarousel *-- _AnimatedCarouselCard
  _MobileCarousel *-- _CarouselCard : 6
  _AnimatedHomePage *-- _AnimatedCategoryItem : 3
  _AnimatedCategoryItem *-- CategoryListItem
  CategoryListItem *-- CategoryDemoItem : one per demo
```

- `◆──` contains

## Open a demo from a category · sequence {#sequence}

Expanding a list and opening a demo are both local: the only shared state is the route name.

```mermaid
sequenceDiagram
  actor User
  participant Home as _AnimatedHomePageState
  participant List as CategoryListItem
  participant Item as CategoryDemoItem
  participant Routes as RouteConfiguration
  participant Demo as DemoPage
  Home->>Home: 150 ms after launch, entrance 800 ms
  User->>List: tap MATERIAL
  List->>List: _handleTap(), expand over 200 ms
  List->>Home: callback saves _isMaterialListExpanded
  User->>Item: tap Buttons
  Item->>Routes: restorablePushNamed /demo/button
  Routes->>Routes: onGenerateRoute() matches the slug pattern
  Routes->>Demo: DemoPage(slug: button)
  Demo-->>User: the demo page slides in
```

## Key files {#files}

- `lib/pages/home.dart` · home page, carousels, study wrapper
- `lib/pages/category_list_item.dart` · expandable category and demo rows
- `lib/routes.dart` · route patterns and study routes
- `lib/data/demos.dart` · studies and demo lists
