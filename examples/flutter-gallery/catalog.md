---
title: Component Catalog Module
sub: The registry of 42 component demos and 81 configurations, each a deferred widget with its generated source code.
card_title: Component catalog
card: 42 Material, Cupertino and reference demos
screenshots:
- file: shots/catalog/01_cards.jpg
  caption: Cards demo
- file: shots/catalog/02_motion.jpg
  caption: 'Motion: container transform'
- file: shots/catalog/03_transformations.jpg
  caption: 2D transformations
---

## What it does {#what}

`Demos` is the app's table of contents: six studies, 24 Material demos, 13 Cupertino demos and 5 reference demos (colors, typography, motion, 2D transformations, two-pane), 81 configurations in all. Each `GalleryDemo` has a title, subtitle, icon, URL slug and category; each of its configurations has a title, a description, an API documentation URL, a `buildRoute` that builds the live widget and a `code` builder. The demo libraries are `deferred` imports, so `buildRoute` wraps the widget in a `DeferredWidget` that loads the library once, caches the future for everyone, and shows an empty placeholder until it arrives. The source shown in the code panel comes from `CodeSegments`, a 50,000-line file generated from the demo files at build time: one highlighted `TextSpan` builder per configuration (64 of them). One demo class usually serves several configurations through a type enum — `ButtonDemo(type: ButtonDemoType.text)` and four siblings share one file.

## Logic · class diagram {#classes}

A demo is data; the widget it shows is created lazily, after its library loads.

```mermaid
classDiagram
  direction LR
  class Demos {
    <<registry>>
    all()
    studies()
    materialDemos()
    cupertinoDemos()
    otherDemos()
    asSlugToDemoMap()
    allDescriptions()
  }
  class GalleryDemo {
    <<data>>
    title · subtitle · icon
    slug · studyId · category
    describe
  }
  class GalleryDemoConfiguration {
    <<data>>
    title · description
    documentationUrl
    buildRoute · code
  }
  class GalleryDemoCategory {
    <<enum>>
    study · material · cupertino · other
    displayTitle()
  }
  class DeferredWidget {
    <<widget>>
    libraryLoader · createWidget · placeholder
    preload()
  }
  class _DeferredWidgetState {
    <<state>>
    _loadedChild
    _onLibraryLoaded()
  }
  class CodeSegments {
    <<generated>>
    buttonDemoText()
    cardsDemo()
  }
  class GalleryIcons { <<icons>> }
  Demos o-- GalleryDemo : all()
  GalleryDemo --> GalleryDemoCategory : category
  GalleryDemo --> GalleryIcons : icon
  GalleryDemo o-- GalleryDemoConfiguration : configurations
  GalleryDemoConfiguration ..> DeferredWidget : buildRoute
  GalleryDemoConfiguration ..> CodeSegments : code
  DeferredWidget --> _DeferredWidgetState : createState
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · a few of the demos {#widgets}

Every demo is an ordinary widget with its own `Scaffold`; enums pick the variant a configuration shows.

```mermaid
classDiagram
  direction TB
  class DemoWrapper { <<widget>> }
  class DeferredWidget { <<loader>> }
  class ButtonDemo {
    <<demo>>
    type
  }
  class ButtonDemoType {
    <<enum>>
    text · elevated · outlined · toggle · floating
  }
  class CardsDemo { <<demo>> }
  class TravelDestinationItem {
    <<widget>>
    destination · shape
  }
  class CupertinoAlertDemo {
    <<demo>>
    type
  }
  class OpenContainerTransformDemo { <<demo>> }
  class TransformationsDemo { <<demo>> }
  DemoWrapper *-- DeferredWidget
  DeferredWidget *-- ButtonDemo
  ButtonDemo --> ButtonDemoType
  DeferredWidget *-- CardsDemo
  CardsDemo *-- TravelDestinationItem
  DeferredWidget *-- CupertinoAlertDemo
  DeferredWidget *-- OpenContainerTransformDemo
  DeferredWidget *-- TransformationsDemo
```

- `◆──` contains
- `──▷` reads model

## Load a demo the first time · sequence {#sequence}

Only the first demo from a library pays for loading it; the future is shared.

```mermaid
sequenceDiagram
  actor User
  participant Page as _GalleryDemoPageState
  participant Config as GalleryDemoConfiguration
  participant Deferred as DeferredWidget
  participant State as _DeferredWidgetState
  participant Button as ButtonDemo
  User->>Page: open /demo/button
  Page->>Config: buildRoute
  Config->>Deferred: DeferredWidget(material library, builder)
  Deferred->>State: initState
  State->>Deferred: preload(), stores the load future once
  State-->>User: empty placeholder
  Deferred-->>State: library loaded
  State->>State: _onLibraryLoaded()
  State->>Button: ButtonDemo(type: text)
  Button-->>User: the live text buttons
```

## Key files {#files}

- `lib/data/demos.dart` · demo registry and configurations
- `lib/deferred_widget.dart` · deferred library loading
- `lib/codeviewer/code_segments.dart` · generated highlighted sources
- `lib/demos/material/` · 24 Material demos
- `lib/demos/cupertino/` · 13 Cupertino demos
- `lib/demos/reference/` · colors, typography, motion, transformations
- `lib/data/icons.dart` · demo icons
