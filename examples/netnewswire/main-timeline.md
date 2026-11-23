---
title: Main Timeline Module
sub: The article list for whichever feed, folder or smart feed is selected, with search and "mark all as read".
card_title: Main Timeline
card: Article list, search, mark as read
screenshots:
- file: shots/main-timeline/01_feed.jpg
  caption: One feed's articles, unread dots on the left
- file: shots/main-timeline/02_mark_all_read.jpg
  caption: Mark All as Read asks first
---

## What it does {#what}

`MainTimelineViewController` reads `coordinator.articles` — whatever the sidebar selection resolved to — and feeds it to a `UICollectionViewDiffableDataSource<Int, Article>` of `MainTimelineCell` rows. A built-in `UISearchController` has two scopes: search this feed, or search everywhere; `showSearchAll()` (reached from the sidebar's search button, a keyboard shortcut, or a Home Screen quick action) activates it straight into the "everywhere" scope. Swiping a row, or a toolbar button, calls `markAllAsRead(_:)`; when more than one article would be marked, `MarkAsReadAlertController` first shows an action-sheet confirmation anchored to wherever the user tapped (a `CGRect`, a `UIView` or a `UIBarButtonItem` — three source types, one alert). Selecting a row calls `coordinator.selectArticle()`, which is how the Article module finds out what to show; it doesn't select the row back the other way. Marking as read updates the row's unread dot without a full reload, since `applyChanges` only runs on real additions/removals.

## Logic · class diagram {#classes}

The view controller is a thin diffable-data-source wrapper; every actual read/unread and selection decision is the coordinator's.

```mermaid
classDiagram
  direction LR
  class MainTimelineViewController {
    <<page>>
    dataSource · coordinator
    applyChanges() · showSearchAll()
    markAllAsRead()
  }
  class SceneCoordinator {
    <<coordinator>>
    articles
    selectArticle() · markAllAsReadInTimeline()
  }
  class MarkAsReadAlertController {
    <<helper>>
    confirm()
  }
  class Article {
    <<model>>
    articleID · title · status
  }
  MainTimelineViewController --> SceneCoordinator : coordinator
  MainTimelineViewController ..> Article : articles, one row each
  MainTimelineViewController ..> MarkAsReadAlertController : confirm()
  MarkAsReadAlertController ..> SceneCoordinator : markAllAsReadInTimeline() on confirm
  SceneCoordinator o-- Article : articles
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · widget composition {#widgets}

```mermaid
classDiagram
  direction TB
  class MainTimelineViewController { <<page>> }
  class MainTimelineCell {
    <<widget>>
    unread dot
  }
  class MainTimelineCellData {
    <<model>>
    title · byline
  }
  MainTimelineViewController *-- MainTimelineCell : one per article
  MainTimelineCell --> MainTimelineCellData : cellData
```

- `◆──` contains
- `──▷` reads model

## Select a feed and mark its articles read · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Sidebar as MainFeedCollectionViewController
  participant Coord as SceneCoordinator
  participant Timeline as MainTimelineViewController
  participant Alert as MarkAsReadAlertController
  User->>Sidebar: tap a feed
  Sidebar->>Coord: selectSidebarItem()
  Coord->>Coord: fetches articles for the selection
  Coord-->>Timeline: articles changes
  Timeline->>Timeline: applyChanges(), rows appear
  User->>Timeline: tap "Mark All as Read"
  Timeline->>Alert: confirm(articlesToMark)
  Alert-->>User: action sheet, anchored to the button
  User->>Alert: confirms
  Alert->>Coord: markAllAsReadInTimeline(articles)
  Coord-->>Timeline: unread dots clear, no reload
```

## Key files {#files}

- `iOS/MainTimeline/MainTimelineViewController.swift` · article list, search, mark as read
- `iOS/MainTimeline/MarkAsReadAlertController.swift` · the confirmation action sheet
- `iOS/MainTimeline/Cell/MainTimelineCell.swift` · one article row
