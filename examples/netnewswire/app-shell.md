---
title: App Shell Module
sub: The three-column split view (feeds · timeline · article), launch, and deep links from widgets, notifications and the `feed:`/`netnewswire:` URL schemes.
card_title: App Shell
card: Launch, the 3-column split view, deep links
screenshots:
- file: shots/app-shell/01_feeds.jpg
  caption: On iPhone the three columns are one navigation stack, opening on the feeds
---

## What it does {#what}

`AppDelegate` starts `AccountManager` before anything else, registers background refresh tasks and notification handling, and imports the default feeds on first run. Each window scene gets its own `SceneDelegate`, which builds one `SceneCoordinator` and hands it the `RootSplitViewController` — a `UISplitViewController` with three columns: the feed sidebar (primary), the article timeline (supplementary) and the reading view (secondary). On iPhone the columns collapse into a single navigation stack instead. A cold launch restores the previous selection unless an external action — a notification tap, a Home Screen quick action, a Siri shortcut, a widget tap, or a `feed:`/`feeds:`/`netnewswire://theme` URL — is pending, in which case that action's navigation wins and selection restoration is skipped so the two don't race. Widget taps for the Today, Starred and Unread smart feeds open that feed and, after a fixed 0.6 s to let the sidebar rebuild, select the specific article by ID.

## Logic · class diagram {#classes}

`SceneCoordinator` is the one object every screen talks to: it owns the three visible view controllers and the sidebar's tree, and is the only thing that knows how to navigate between them.

```mermaid
classDiagram
  direction LR
  class AppDelegate {
    <<app delegate>>
    unreadCount
    registerBackgroundTasks()
    prepareAccountsForBackground()
    prepareAccountsForForeground()
  }
  class SceneDelegate {
    <<scene delegate>>
    coordinator
    handleShortcutItem()
    scene(openURLContexts:)
  }
  class SceneCoordinator {
    <<coordinator>>
    rootSplitViewController · mainFeedCollectionViewController
    mainTimelineViewController · articleViewController
    treeController · webViewProvider
    selectSidebarItem() · selectArticle()
    selectArticleInCurrentFeed() · showSearch()
    showAddFeed() · showSettings()
    restoreWindowState() · handle()
  }
  class RootSplitViewController {
    <<split view>>
    coordinator
    showColumn()
  }
  class MainFeedCollectionViewController { <<page>> }
  class MainTimelineViewController { <<page>> }
  class ArticleViewController { <<page>> }
  class AccountManager {
    <<service>>
    shared
    start()
  }
  SceneDelegate --> SceneCoordinator : coordinator
  SceneDelegate ..> AppDelegate : resumeIfNecessary()
  SceneCoordinator --> RootSplitViewController : rootSplitViewController
  RootSplitViewController --> SceneCoordinator : coordinator, delegate
  SceneCoordinator --> MainFeedCollectionViewController : mainFeedCollectionViewController
  SceneCoordinator --> MainTimelineViewController : mainTimelineViewController
  SceneCoordinator --> ArticleViewController : articleViewController
  AppDelegate ..> AccountManager : start()
  SceneCoordinator ..> AccountManager : shared.unreadCount
```

- `──▷` holds
- `┄┄▷` uses

## Screen · widget composition {#widgets}

One split view, three columns; the coordinator decides which columns show at once from the current `displayMode`.

```mermaid
classDiagram
  direction TB
  class RootSplitViewController { <<split view>> }
  class MainFeedCollectionViewController { <<primary column>> }
  class MainTimelineViewController { <<supplementary column>> }
  class ArticleViewController { <<secondary column>> }
  RootSplitViewController *-- MainFeedCollectionViewController : primary
  RootSplitViewController *-- MainTimelineViewController : supplementary
  RootSplitViewController *-- ArticleViewController : secondary
```

- `◆──` contains

## Open an article from a Home Screen widget · sequence {#sequence}

A widget tap always carries the smart feed's URL plus the article's ID as a query item.

```mermaid
sequenceDiagram
  actor User
  participant Widget as Home Screen widget
  participant Scene as SceneDelegate
  participant Coord as SceneCoordinator
  participant Timeline as MainTimelineViewController
  participant Article as ArticleViewController
  User->>Widget: tap an unread article
  Widget->>Scene: scene(openURLContexts:) with the Unread widget URL + id
  Scene->>Coord: selectAllUnreadFeed()
  Note over Scene: waits 0.6 s for the sidebar and timeline to rebuild
  Scene->>Coord: selectArticleInCurrentFeed(id)
  Coord->>Coord: finds the article in the current timeline
  Coord->>Timeline: updateArticleSelection() highlights the row
  Coord->>Article: article, loads it
  Article-->>User: article shown, or timeline-only on iPhone
```

## Key files {#files}

- `iOS/AppDelegate.swift` · app launch, background refresh, notifications
- `iOS/SceneDelegate.swift` · per-window scene, deep-link URL handling
- `iOS/SceneCoordinator.swift` · navigation, selection, search, sidebar state (~2,800 lines)
- `iOS/RootSplitViewController.swift` · the 3-column `UISplitViewController`
