---
title: Demo Page Module
sub: One page for every component demo, with an options, info, code and documentation panel above the live demo.
card_title: Demo page
card: Live demo with options, info and source code
screenshots:
- file: shots/demo/01_feature_discovery.jpg
  caption: 'First demo with options: the feature-discovery overlay'
- file: shots/demo/02_options.jpg
  caption: 'Options: one row per configuration'
- file: shots/demo/03_info.jpg
  caption: 'Info: the configuration''s description'
- file: shots/demo/04_code.jpg
  caption: 'Code: generated, highlighted source with COPY ALL'
---

## What it does {#what}

`/demo/<slug>` looks the slug up in the demos registry (an unknown slug pops back to home) and shows the demo's current configuration live, under its own Material theme. The app bar has up to five buttons: **options** (only when the demo has more than one configuration), **info**, **code**, **documentation** (opens the API page in the browser, or shows the URL in a dialog if it can't) and, on desktop, **fullscreen**. On a phone the chosen panel grows above the demo over 200 ms and pushes it down; tapping the same button again, or tapping the demo, closes it, and picking a configuration in options switches the demo and closes the panel. The code panel shows the configuration's syntax-highlighted source in Roboto Mono on a dark background with a **COPY ALL** button that puts the plain text on the clipboard and confirms with a snackbar. The selected panel and configuration survive state restoration. The first time any demo with options opens on a phone, a feature-discovery overlay rings the options button and explains it; that flag is saved on the device, so it never shows again.

## Logic · class diagram {#classes}

The route widget only resolves the slug; the stateful page keeps the panel and configuration as restorable integers.

```mermaid
classDiagram
  direction LR
  class DemoPage {
    <<page>>
    slug
    baseRoute
  }
  class _DemoPageState {
    <<page state>>
    slugToDemoMap
  }
  class GalleryDemoPage { <<page>> }
  class _GalleryDemoPageState {
    <<page state>>
    _demoStateIndex · _configIndex
    _currentConfig · _hasOptions
    _handleTap()
    setStateAndUpdate()
    _resolveState()
    _showDocumentation()
  }
  class _DemoState {
    <<enum>>
    normal · options · info · code · fullscreen
  }
  class Demos {
    <<registry>>
    asSlugToDemoMap()
  }
  class GalleryDemo {
    <<data>>
    title · configurations
  }
  class GalleryDemoConfiguration {
    <<data>>
    title · description · documentationUrl
    buildRoute · code
  }
  class FeatureDiscoveryController {
    <<widget>>
    isLocked
    lock() · unlock()
  }
  DemoPage --> _DemoPageState : createState
  _DemoPageState ..> Demos : asSlugToDemoMap()
  _DemoPageState ..> GalleryDemoPage : demo
  GalleryDemoPage --> _GalleryDemoPageState : createState
  _GalleryDemoPageState --> _DemoState : _demoStateIndex
  _GalleryDemoPageState --> GalleryDemo : demo
  GalleryDemo o-- GalleryDemoConfiguration : configurations
  _GalleryDemoPageState *-- FeatureDiscoveryController
```

- `──▷` holds
- `◇──` list of
- `◆──` contains
- `┄┄▷` uses

## Screen · widget composition {#widgets}

On a phone the page is a non-scrolling list — panel, then demo — so the panel's growth slides the demo down.

```mermaid
classDiagram
  direction TB
  class GalleryDemoPage { <<page>> }
  class FeatureDiscovery {
    <<widget>>
    title · description · showOverlay
  }
  class _DemoSectionOptions {
    <<panel>>
    configurations · configIndex
  }
  class _DemoSectionOptionsItem {
    <<widget>>
    title · isSelected
  }
  class _DemoSectionInfo {
    <<panel>>
    title · description
  }
  class _DemoSectionCode { <<panel>> }
  class CodeDisplayPage {
    <<widget>>
    code
  }
  class CodeStyle { <<inherited>> }
  class DemoWrapper {
    <<widget>>
    buildRoute
  }
  class ApplyTextOptions { <<widget>> }
  GalleryDemoPage *-- FeatureDiscovery : options button
  GalleryDemoPage *-- _DemoSectionOptions
  _DemoSectionOptions *-- _DemoSectionOptionsItem
  GalleryDemoPage *-- _DemoSectionInfo
  GalleryDemoPage *-- CodeStyle
  CodeStyle *-- _DemoSectionCode
  _DemoSectionCode *-- CodeDisplayPage
  GalleryDemoPage *-- DemoWrapper : the live demo
  DemoWrapper *-- ApplyTextOptions
```

- `◆──` contains

## Panels · state machine {#states}

Each button toggles its own panel; on a phone everything leads back to the plain demo.

```mermaid
stateDiagram-v2
  [*] --> normal
  normal --> options : tune button
  normal --> info : info button
  normal --> code : code button
  options --> normal : same button, tap the demo, or pick a configuration
  info --> normal : same button or tap the demo
  code --> normal : same button or tap the demo
  options --> info : info button
  info --> code : code button
  code --> options : tune button
  normal --> fullscreen : desktop only
  fullscreen --> options : fullscreen again, desktop
```

## Read a demo's code · sequence {#sequence}

The code is not read from files at run time: each configuration carries a generated `TextSpan` builder.

```mermaid
sequenceDiagram
  actor User
  participant Page as _GalleryDemoPageState
  participant Config as GalleryDemoConfiguration
  participant Code as CodeDisplayPage
  participant Segments as CodeSegments
  User->>Page: tap the code button
  Page->>Page: _handleTap(code)
  Page->>Page: setStateAndUpdate(), code panel opens
  Page->>Config: code
  Page->>Code: CodeDisplayPage(code)
  Code->>Segments: buttonDemoText()
  Segments-->>Code: highlighted TextSpan
  Code-->>User: source in the panel
  User->>Code: tap COPY ALL
  Code->>Code: copies the plain text to the clipboard
  Code-->>User: snackbar confirms the copy
```

## Key files {#files}

- `lib/pages/demo.dart` · demo page, panels, code page
- `lib/feature_discovery/` · first-run options overlay
- `lib/codeviewer/` · code style and display types
- `lib/themes/material_demo_theme_data.dart` · theme around demos
