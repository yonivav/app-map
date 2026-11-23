---
title: Main Feed Module
sub: The sidebar of accounts, smart feeds, feeds and folders; adding a feed or folder, and inspecting one.
card_title: Main Feed
card: The feeds/folders sidebar, add, inspect
---

## What it does {#what}

`MainFeedCollectionViewController` renders the sidebar as a `UICollectionViewDiffableDataSource` over a `TreeController`: one section per account, each holding its smart feeds (Today, All Unread, Starred) and the account's feeds and folders, indented by nesting. Folders carry a disclosure triangle (`MainFeedCollectionViewFolderCell`); a feed or container row shows an unread count once it has one (`UILabel+UnreadCount`). Pull-to-refresh and the toolbar refresh button both drive `RefreshProgressView`, a small inline spinner-and-count view. Tapping a row calls `coordinator.selectSidebarItem()`, which is how every other screen finds out what's selected. "Add Feed" and "Add Folder" are SwiftUI sheets (`AddFeedView`, `AddFolderView`) hosted from UIKit with `UIHostingController`; adding a feed accepts a URL typed in, pasted, or carried over from a `feed:` deep link, defaulting the account/folder to whichever one the Settings "Default add location" points at. "Get Info" on a feed or account opens a form-sheet inspector — `FeedInspectorViewController` (a `UITableViewController`, built from a storyboard) for a feed, or the SwiftUI `AccountInspectorView`/`AccountNotificationInspectorView` for an account.

## Logic · class diagram {#classes}

The view controller owns the diffable data source and a `TreeController`'s snapshot of expanded/collapsed containers; it asks the coordinator for everything about selection and navigation.

```mermaid
classDiagram
  direction LR
  class MainFeedCollectionViewController {
    <<page>>
    dataSource · coordinator
    add() · showFeedInspector()
  }
  class SceneCoordinator {
    <<coordinator>>
    selectSidebarItem() · showAddFeed()
    showFeedInspector() · showAccountInspector()
    isExpanded() · expand() · collapse()
  }
  class AddFeedView {
    <<page>>
    urlString · name · container
  }
  class AddFolderView { <<page>> }
  class FeedInspectorViewController {
    <<page>>
    feed
  }
  class AccountInspectorView {
    <<page>>
    account · isModal
  }
  class SmartFeedsController {
    <<service>>
    shared
  }
  class Account {
    <<model>>
    name · type
  }
  class Feed {
    <<model>>
    name · url · unreadCount
  }
  MainFeedCollectionViewController --> SceneCoordinator : coordinator
  MainFeedCollectionViewController ..> SmartFeedsController : shared, for every account's smart feeds
  SceneCoordinator ..> AddFeedView : showAddFeed(), UIHostingController
  SceneCoordinator ..> AddFolderView : showAddFolder(), UIHostingController
  SceneCoordinator ..> FeedInspectorViewController : showFeedInspector()
  SceneCoordinator ..> AccountInspectorView : showAccountInspector(), via UIHostingController
  FeedInspectorViewController --> Feed : feed
  AccountInspectorView --> Account : account
  MainFeedCollectionViewController o-- Account : one section per account
  Account o-- Feed : feeds and folders
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · widget composition {#widgets}

```mermaid
classDiagram
  direction TB
  class MainFeedCollectionViewController { <<page>> }
  class MainFeedCollectionViewCell {
    <<widget>>
    feed row, unread count
  }
  class MainFeedCollectionViewFolderCell {
    <<widget>>
    disclosure triangle
  }
  class MainFeedCollectionHeaderReusableView { <<widget>> }
  class RefreshProgressView {
    <<widget>>
    refresh spinner + count
  }
  MainFeedCollectionViewController *-- MainFeedCollectionViewCell : feed/account rows
  MainFeedCollectionViewController *-- MainFeedCollectionViewFolderCell : folder rows
  MainFeedCollectionViewController *-- MainFeedCollectionHeaderReusableView : section headers
  MainFeedCollectionViewController *-- RefreshProgressView : toolbar
```

- `◆──` contains

## Add a feed by URL · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Sidebar as MainFeedCollectionViewController
  participant Coord as SceneCoordinator
  participant AddView as AddFeedView
  participant Host as UIHostingController
  User->>Sidebar: tap Add
  Sidebar->>Coord: showAddFeed()
  Coord->>Host: wraps AddFeedView in a UIHostingController
  Host-->>User: form sheet with URL, name, account/folder
  User->>AddView: enters URL, taps Subscribe
  AddView->>AddView: isAdding = true, validates and fetches the feed
  AddView-->>Host: dismiss() on success
  Note over AddView: an invalid or unreachable URL sets errorMessage instead of dismissing
  Host-->>Sidebar: sidebar rebuilds with the new feed selected
```

## Key files {#files}

- `iOS/MainFeed/MainFeedCollectionViewController.swift` · the sidebar, its diffable data source
- `iOS/MainFeed/Collection View Cells/` · feed, folder and header cells
- `iOS/MainFeed/RefreshProgressView.swift` · the inline refresh spinner
- `iOS/Add/AddFeedView.swift` · subscribe by URL
- `iOS/Add/AddFolderView.swift` · new folder
- `iOS/Inspector/FeedInspectorViewController.swift` · feed "Get Info"
- `iOS/Inspector/AccountInspectorView.swift` · account "Get Info"
