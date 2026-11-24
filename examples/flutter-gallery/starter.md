---
title: Starter App Study
sub: The smallest study, a template app with an adaptive app bar, a nine-item drawer and a floating add button.
card_title: Starter app
card: A responsive starting layout
screenshots:
- file: shots/starter/01_home.jpg
  caption: Headline, body text and the add button
- file: shots/starter/02_drawer.jpg
  caption: The nine-item drawer, Item 3 selected
---

## What it does {#what}

The Starter app is a single-route `MaterialApp` at `/starter` with its own purple colour scheme, meant as a starting point for a responsive app. On a phone it shows an app bar with share, favourite and search buttons, a drawer, a headline, subtitle and body text, and a round **+** button; on desktop the drawer stays open as a side list, the app bar is 128 pt tall and the button becomes an extended **+ BUTTON**. The drawer has a title, a subtitle and nine items; tapping one highlights it (`selectedItem`), and that is the app's only state. The buttons have no actions.

## Logic · class diagram {#classes}

Three widgets and one integer of state.

```mermaid
classDiagram
  direction LR
  class StarterApp {
    <<app>>
    defaultRoute
  }
  class AdaptiveAppBar {
    <<widget>>
    isDesktop
    preferredSize
  }
  class ListDrawer { <<widget>> }
  class _ListDrawerState {
    <<state>>
    numItems · selectedItem
  }
  StarterApp *-- AdaptiveAppBar
  StarterApp *-- ListDrawer
  ListDrawer --> _ListDrawerState : createState
```

- `◆──` contains
- `──▷` holds

## Pick a drawer item · sequence {#sequence}

The drawer keeps its own selection; nothing else changes.

```mermaid
sequenceDiagram
  actor User
  participant Bar as AdaptiveAppBar
  participant Drawer as ListDrawer
  participant State as _ListDrawerState
  User->>Bar: tap the menu button
  Bar-->>Drawer: Scaffold opens the drawer
  Drawer->>State: build nine items
  User->>State: tap Item 3
  State->>State: setState, selectedItem = 2
  State-->>User: Item 3 highlighted
```

## Key files {#files}

- `lib/studies/starter/app.dart` · Starter app and colour scheme
- `lib/studies/starter/home.dart` · home, adaptive app bar, drawer
