---
title: Flutter Gallery App Map
sub: How the app works, one module at a time · **tap a module or a box** to open its map
modules:
- splash
- home
- settings
- demo
- catalog
- reply
- shrine
- rally
- crane
- fortnightly
- starter
links:
  screens:
    SplashN: splash
    HomeN: home
    SettingsN: settings
    DemoN: demo
    CodeN: demo
    CatalogN: catalog
    ReplyN: reply
    ComposeN: reply
    ShrineLoginN: shrine
    ShrineN: shrine
    CartN: shrine
    RallyLoginN: rally
    RallyN: rally
    RallyDetailsN: rally
    CraneN: crane
    FortnightlyN: fortnightly
    StarterN: starter
  services:
    SplashS: splash
    HomeS: home
    SettingsS: settings
    DemoS: demo
    CatalogS: catalog
    ReplyS: reply
    ShrineS: shrine
    RallyS: rally
    CraneS: crane
    FortnightlyS: fortnightly
    StarterS: starter
---

## Screens · how the user moves

`MaterialApp.onGenerateRoute` matches each route name against a list of regular expressions: `/demo/<slug>` opens one component demo, each study has its own prefix (`/reply`, `/shrine`, `/rally`, `/crane`, `/fortnightly`, `/starter`), and everything else falls through to `/`, the home screen inside the splash and settings layers. Every study is a separate `MaterialApp` with its own routes and theme, wrapped in a floating **Back** button that pops straight to `/`.

```mermaid
flowchart TB
  subgraph splash [Splash]
    SplashN["Splash effect<br/>SplashPage"]
  end
  subgraph home [Home]
    HomeN["Gallery /<br/>HomePage"]
  end
  subgraph settings [Settings]
    SettingsN["Settings panel<br/>SettingsPage"]
  end
  subgraph demo [Demo page]
    DemoN["Demo /demo/slug<br/>GalleryDemoPage"]
    CodeN["Code<br/>CodeDisplayPage"]
  end
  subgraph catalog [Component catalog]
    CatalogN["42 demos<br/>Demos"]
  end
  subgraph reply [Reply]
    ReplyN["Inbox /reply<br/>ReplyApp"]
    ComposeN["Compose<br/>ComposePage"]
  end
  subgraph shrine [Shrine]
    ShrineLoginN["Sign in /shrine/login"]
    ShrineN["Products /shrine<br/>ProductPage"]
    CartN["Cart<br/>ShoppingCartPage"]
  end
  subgraph rally [Rally]
    RallyLoginN["Sign in /rally/login"]
    RallyN["Five tabs /rally<br/>OverviewView"]
    RallyDetailsN["Category details<br/>FinancialEntityCategoryDetailsPage"]
  end
  subgraph crane [Crane]
    CraneN["Fly · Sleep · Eat /crane<br/>CraneApp"]
  end
  subgraph fortnightly [Fortnightly]
    FortnightlyN["News /fortnightly<br/>FortnightlyApp"]
  end
  subgraph starter [Starter app]
    StarterN["Starter /starter<br/>StarterApp"]
  end
  HomeN -->|fling the top edge down| SplashN
  SplashN -->|tap or fling up| HomeN
  HomeN -->|settings icon| SettingsN
  HomeN -->|tap a demo in a category| DemoN
  DemoN -->|code button| CodeN
  DemoN -->|builds the configuration| CatalogN
  HomeN -->|carousel card| ReplyN
  HomeN -->|carousel card| ShrineLoginN
  HomeN -->|carousel card| RallyLoginN
  HomeN -->|carousel card| CraneN
  HomeN -->|carousel card| FortnightlyN
  HomeN -->|carousel card| StarterN
  ReplyN -->|FAB| ComposeN
  ShrineLoginN -->|NEXT| ShrineN
  ShrineN -->|cart tab| CartN
  RallyLoginN -->|LOGIN| RallyN
  RallyN -->|tap a category| RallyDetailsN
```

- `───▷` opens
- `▭` tap to open its module

## Services · what the screens share

There is no service layer: the Gallery's shared state is one immutable `GalleryOptions` value held by an InheritedWidget (`ModelBinding`) above the root `MaterialApp`, and every screen and study reads it. Demos and their code come from static registries compiled into the app, most of them behind deferred imports; only the first-run tooltip flag is written to disk.

```mermaid
flowchart LR
  subgraph Screens
    SplashS["Splash"]
    HomeS["Home"]
    SettingsS["Settings"]
    DemoS["Demo page"]
    CatalogS["Catalog"]
    ReplyS["Reply"]
    ShrineS["Shrine"]
    RallyS["Rally"]
    CraneS["Crane"]
    FortnightlyS["Fortnightly"]
    StarterS["Starter"]
  end
  subgraph Shared ["app-wide state and registries"]
    Options["GalleryOptions"]
    Binding["ModelBinding"]
    DemosR["Demos"]
    Deferred["DeferredWidget"]
    Code["CodeSegments"]
    Discovery["FeatureDiscovery"]
    Wrapper["StudyWrapper"]
    TextOpts["ApplyTextOptions"]
  end
  subgraph Disk ["on the device"]
    Storage["GetStorage"]
  end
  SettingsS -->|updateModel| Binding
  Binding -->|currentModel| Options
  HomeS -->|materialDemos| DemosR
  HomeS -->|toggles| SplashS
  DemoS -->|asSlugToDemoMap| DemosR
  DemoS -->|showOverlay| Discovery
  Discovery -->|feature_highlight_shown| Storage
  CatalogS -->|preload| Deferred
  CatalogS -->|buttonDemoText| Code
  ReplyS -->|study| Wrapper
  ShrineS -->|study| Wrapper
  RallyS -->|study| Wrapper
  CraneS -->|study| Wrapper
  FortnightlyS -->|study| Wrapper
  StarterS -->|study| Wrapper
  Wrapper -->|child| TextOpts
  TextOpts -->|textScaleFactor| Options
  RallyS -->|loadLibrary| Deferred
  ShrineS -->|loadLibrary| Deferred
  CraneS -->|loadLibrary| Deferred
  FortnightlyS -->|loadLibrary| Deferred
```

- `───▷` calls or holds, labelled with the method or field
- `▭` tap to open its module
