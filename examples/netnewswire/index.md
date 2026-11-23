---
title: NetNewsWire App Map
sub: How the iOS app works, one module at a time · **tap a module or a box** to open its map
modules:
- app-shell
- main-feed
- main-timeline
- article
- settings
- share-extension
links:
  screens:
    ShellN: app-shell
    FeedN: main-feed
    TimelineN: main-timeline
    ArticleN: article
    SettingsN: settings
    ShareN: share-extension
  services:
    ShellS: app-shell
    FeedS: main-feed
    TimelineS: main-timeline
    ArticleS: article
    SettingsS: settings
    ShareS: share-extension
---

## Screens · how the user moves

The app opens straight into the 3-column split view the App Shell owns — sidebar, timeline, article — restoring the last selection unless a notification, widget, Siri shortcut or `feed:`/`netnewswire://` URL is pending, in which case that wins instead. On iPhone the three columns collapse into one navigation stack, so the same moves become pushes.

```mermaid
flowchart TB
  subgraph shell [App Shell]
    ShellN["Launch, deep links<br/>SceneCoordinator"]
  end
  subgraph feed [Main Feed]
    FeedN["Sidebar<br/>MainFeedCollectionViewController"]
    AddN["Add feed/folder<br/>AddFeedView"]
    InspectN["Get Info<br/>FeedInspectorViewController"]
  end
  subgraph timeline [Main Timeline]
    TimelineN["Article list<br/>MainTimelineViewController"]
  end
  subgraph article [Article]
    ArticleN["Reading view<br/>ArticleViewController"]
  end
  subgraph settings [Settings]
    SettingsN["Settings<br/>SettingsView"]
  end
  subgraph share [Share Extension]
    ShareN["Add from another app<br/>ShareAddFeedViewController"]
  end
  ShellN -->|restores selection, or a deep link| FeedN
  ShellN -.->|feed: URL, or widget tap with an article id| TimelineN
  FeedN -->|tap a feed or smart feed| TimelineN
  FeedN -->|tap Add| AddN
  FeedN -->|Get Info| InspectN
  TimelineN -->|tap a row| ArticleN
  FeedN -->|gear icon| SettingsN
  SettingsN -->|Add Account| InspectN
  ShareN -.->|writes a shared request the app reads on resume| ShellN
```

- `───▷` opens
- `┈┈▷` a hand-off through shared state, not a direct call
- `▭` tap to open its module

## Services · what the screens talk through

Only `SceneCoordinator` is shared by every screen — it's the sole owner of the three visible view controllers and the only thing that knows how to navigate between them. Everything below it is reached by exactly the modules that need it: the article reader needs a pooled `WKWebView` and a reader-mode extractor; the share extension and the Siri "Add Feed" shortcut can't call `AccountManager` directly (separate processes), so they both leave a request in `ExtensionFeedAddRequestFile` for the main app to pick up.

```mermaid
flowchart LR
  subgraph Screens
    ShellS["App Shell"]
    FeedS["Main Feed"]
    TimelineS["Main Timeline"]
    ArticleS["Article"]
    SettingsS["Settings"]
    ShareS["Share Extension"]
  end
  subgraph Nav ["navigation"]
    Coord["SceneCoordinator"]
  end
  subgraph Data ["accounts and feeds"]
    AM["AccountManager"]
    Smart["SmartFeedsController"]
  end
  subgraph Reading ["article reading"]
    WVP["WebViewProvider"]
    Extractor["ArticleExtractor"]
  end
  subgraph Handoff ["cross-process hand-off"]
    ReqFile["ExtensionFeedAddRequestFile"]
  end
  subgraph Notify ["notifications"]
    UNM["UserNotificationManager"]
  end
  ShellS -->|owns| Coord
  FeedS -->|selectSidebarItem| Coord
  TimelineS -->|selectArticle| Coord
  ArticleS -->|article| Coord
  Coord -->|shared.unreadCount| AM
  FeedS -->|one section per account| AM
  SettingsS -->|createAccount| AM
  FeedS -->|every account's smart feeds| Smart
  ArticleS -->|dequeueWebView| WVP
  ArticleS -->|toggleArticleExtractor| Extractor
  ShareS -->|save| ReqFile
  ShellS -->|shared.start, reads it back| ReqFile
  ShellS -->|start| UNM
```

- `───▷` calls, labelled with the method
- `▭` tap to open its module
