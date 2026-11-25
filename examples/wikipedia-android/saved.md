---
title: Saved Module
sub: The Saved tab — all saved articles and your reading lists, downloaded for offline reading by one worker and synced with your account by another.
card_title: Saved
card: Saved articles, lists, offline and sync
screenshots:
- file: shots/saved/01_all.jpg
  caption: All articles, with the article just saved
- file: shots/saved/02_lists.jpg
  caption: Reading lists, with the recommended-list card
---

## What it does {#what}

`ReadingListsFragment` hosts the Compose `ReadingListsScreen` with two tabs, **All articles** and **Collections** (your reading lists), a search action mode, sort options and an overflow menu to create, import, select or refresh lists. All articles can be filtered to those not in any collection. Saving an article anywhere inserts a `ReadingListPage` into the default list through `ReadingListPageDao`, which enqueues `SavedPageSyncService`: a WorkManager worker that downloads each waiting page's mobile HTML and media for offline reading, reporting progress back to the rows. When you are logged in (and sync is on and not disabled by remote config), `ReadingListSyncAdapter` — another worker — merges local and remote lists both ways through `ReadingListClient`: it pulls changes since the last sync, applies local deletions, creates or updates remote lists and entries, and stores the new sync time. Pulling down forces a sync; reaching the list limit shows a message. Tapping a list opens `ReadingListActivity`; tapping an article opens it. A **Discover** card can generate a recommended reading list from your interests.

## Logic · class diagram {#classes}

The screen only reads Room through its view model; two workers do all the network work in the background.

```mermaid
classDiagram
  direction LR
  class ReadingListsFragment {
    <<page>>
    onRefresh()
    startSearchActionMode()
    showReadingListsOverflowMenu()
  }
  class ReadingListsViewModel {
    <<view-model>>
    setSelectedTab()
    setArticleFilter()
    setSearchQuery()
    updatePageDownloadProgress()
  }
  class SavedTab {
    <<enum>>
    ALL_ARTICLES · COLLECTIONS
  }
  class ReadingList {
    <<entity>>
    listTitle · pages · remoteId
  }
  class ReadingListPage {
    <<entity>>
    apiTitle · offline · status
  }
  class ReadingListPageDao {
    <<dao>>
    addPagesToList()
  }
  class SavedPageSyncService {
    <<worker>>
    doWork()
    savePageFor()
    enqueue()
  }
  class ReadingListSyncAdapter {
    <<worker>>
    doWork()
    manualSync()
    manualSyncWithForce()
  }
  class ReadingListClient {
    <<API client>>
    getChangesSince()
    createList()
  }
  ReadingListsFragment --> ReadingListsViewModel
  ReadingListsViewModel --> SavedTab : selected tab
  ReadingList o-- ReadingListPage : pages
  ReadingListPageDao ..> SavedPageSyncService : enqueue()
  SavedPageSyncService ..> ReadingListPage : downloads, marks offline
  ReadingListsFragment ..> ReadingListSyncAdapter : manualSyncWithForce()
  ReadingListSyncAdapter --> ReadingListClient
  ReadingListSyncAdapter ..> ReadingList : merges local and remote
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · composition {#widgets}

```mermaid
classDiagram
  direction TB
  class ReadingListsFragment { <<page>> }
  class ReadingListsScreen { <<composable>> }
  class SavedTabBar { <<composable>> }
  class ReadingListsContent { <<composable>> }
  class ReadingListsList { <<composable>> }
  class ReadingListRow { <<composable>> }
  class ReadingListPageRow { <<composable>> }
  class DiscoverCard { <<composable>> }
  ReadingListsFragment *-- ReadingListsScreen
  ReadingListsScreen *-- SavedTabBar
  ReadingListsScreen *-- ReadingListsContent
  ReadingListsContent *-- ReadingListsList
  ReadingListsList *-- ReadingListRow : collections
  ReadingListsList *-- ReadingListPageRow : all articles
  ReadingListsContent *-- DiscoverCard
```

- `◆──` contains

## Save an article and sync it · sequence {#sequence}

The database insert is the trigger: everything after it runs in workers.

```mermaid
sequenceDiagram
  actor User
  participant Article as PageFragment
  participant Dao as ReadingListPageDao
  participant Offline as SavedPageSyncService
  participant Sync as ReadingListSyncAdapter
  participant Client as ReadingListClient
  User->>Article: tap Save
  Article->>Dao: addPagesToList(), default list
  Dao->>Offline: enqueue()
  Offline->>Offline: savePageFor(), HTML and media
  Dao->>Sync: manualSync()
  Sync->>Client: getChangesSince()
  Sync->>Client: creates the remote entry
  Sync-->>User: Saved tab shows it, available offline
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/readinglist/ReadingListsFragment.kt` · Saved tab
- `app/src/main/java/org/wikipedia/readinglist/ReadingListsViewModel.kt` · lists, articles, filters
- `app/src/main/java/org/wikipedia/readinglist/compose/` · Saved screen in Compose
- `app/src/main/java/org/wikipedia/readinglist/database/` · list and page entities
- `app/src/main/java/org/wikipedia/readinglist/db/` · DAOs
- `app/src/main/java/org/wikipedia/readinglist/sync/` · account sync worker and API client
- `app/src/main/java/org/wikipedia/savedpages/SavedPageSyncService.kt` · offline downloads
