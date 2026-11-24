---
title: Saved Module
sub: The Saved tab — every saved article for offline reading, and reading lists that sync with your Wikipedia account.
card_title: Saved
card: Saved articles and synced reading lists
screenshots:
- file: shots/saved/01_all.jpg
  caption: 'All articles: the article saved from its toolbar'
- file: shots/saved/02_lists.jpg
  caption: Reading lists, empty until you make one
---

## What it does {#what}

`SavedCoordinator` builds the Saved tab as one SwiftUI screen, `WMFSavedHostingController`, with two segments: **All articles** and **Reading lists**. Saving an article anywhere (the article toolbar, a feed card, a map popover) toggles it in `MWKSavedPageList`; `SavedArticlesFetcher` then downloads each saved article with its images for offline reading, at most 12 downloads a minute, and backs off when the server answers busy. All articles lists them newest first or by title, with search, a download-progress banner, an edit mode to select several (remove, add to a list) and per-article alerts (not yet downloaded, list limit reached). Reading lists shows your lists — **Saved** is the default one — and opens a list's detail screen; **+** creates a list. When you are logged in, `WMFReadingListsController` syncs lists and their entries with the reading-lists API both ways, and pulling down runs a full sync. Each segment's sort order is remembered.

## Logic · class diagram {#classes}

The SwiftUI side never touches Core Data: it reads plain models from data controllers that the app-side coordinators feed.

```mermaid
classDiagram
  direction LR
  class SavedCoordinator {
    <<coordinator>>
    start()
    makeSavedViewController()
  }
  class WMFSavedViewModel {
    <<view-model>>
    segment · sortOrder · isEditing
    selectSegment()
    setSortOrder()
    toggleEditing()
  }
  class SavedAllArticlesCoordinator {
    <<coordinator>>
    viewModel
    showArticle()
    deleteSavedArticles()
  }
  class WMFSavedAllArticlesViewModel {
    <<view-model>>
    articles · filteredArticles · state
    loadArticles()
    toggleSelection()
  }
  class ReadingListsCoordinator {
    <<coordinator>>
    presentCreateReadingList()
    showDetail()
  }
  class WMFReadingListsViewModel {
    <<view-model>>
    readingLists · state
    loadReadingLists()
    refresh()
  }
  class WMFLegacyReadingListsDataController { <<data controller>> }
  class LegacyReadingListsDataSource {
    <<adapter>>
    unsaveConfirmation
  }
  class WMFReadingListsController {
    <<sync service>>
    maxEntriesPerList · maxListsPerUser
    fullSync()
    createReadingList()
    userSave() · unsave()
  }
  class SavedArticlesFetcher {
    <<downloader>>
    maximumDownloadsPerMinute
    start() · stop()
  }
  SavedCoordinator ..> WMFSavedViewModel : creates
  SavedCoordinator --> SavedAllArticlesCoordinator
  SavedCoordinator --> ReadingListsCoordinator
  WMFSavedViewModel --> WMFSavedAllArticlesViewModel : allArticlesViewModel
  WMFSavedViewModel --> WMFReadingListsViewModel : readingListsViewModel
  SavedAllArticlesCoordinator ..> WMFSavedAllArticlesViewModel : viewModel
  WMFSavedAllArticlesViewModel --> WMFLegacyReadingListsDataController : dataController
  WMFLegacyReadingListsDataController --> LegacyReadingListsDataSource : delegate
  SavedAllArticlesCoordinator ..> WMFReadingListsController : fullSync() · unsave()
  ReadingListsCoordinator ..> WMFReadingListsController : createReadingList()
```

- `──▷` holds
- `┄┄▷` uses

## Screen · view composition {#widgets}

```mermaid
classDiagram
  direction TB
  class WMFSavedHostingController { <<hosting>> }
  class WMFSavedView { <<SwiftUI>> }
  class WMFSavedProgressView { <<banner>> }
  class WMFSavedAllArticlesView { <<SwiftUI>> }
  class WMFReadingListsView { <<SwiftUI>> }
  class WMFReadingListRow { <<row>> }
  class ReadingListDetailViewController { <<page>> }
  WMFSavedHostingController *-- WMFSavedView
  WMFSavedView *-- WMFSavedProgressView
  WMFSavedView *-- WMFSavedAllArticlesView : All articles
  WMFSavedView *-- WMFReadingListsView : Reading lists
  WMFReadingListsView *-- WMFReadingListRow
  WMFReadingListRow ..> ReadingListDetailViewController : opens
```

- `◆──` contains
- `┄┄▷` opens

## Save an article, read it offline · sequence {#sequence}

Saving is instant and local; the download and the account sync happen afterwards in the background.

```mermaid
sequenceDiagram
  actor User
  participant Article as ArticleViewController
  participant Pages as MWKSavedPageList
  participant Fetcher as SavedArticlesFetcher
  participant Sync as WMFReadingListsController
  participant All as WMFSavedAllArticlesViewModel
  User->>Article: tap Save
  Article->>Pages: toggles the saved page
  Pages->>Sync: userSave(), adds it to the default list
  Sync->>Sync: syncs with your account when logged in
  Sync-->>Fetcher: a saved article without a download
  Fetcher->>Fetcher: downloads HTML and images, 12 a minute
  User->>All: open Saved
  All->>All: loadArticles()
  All-->>User: newest first, ready offline
```

## Key files {#files}

- `Wikipedia/Code/SavedCoordinator.swift` · builds the Saved tab
- `Wikipedia/Code/SavedAllArticlesCoordinator.swift` · all-articles actions
- `Wikipedia/Code/ReadingListsCoordinator.swift` · reading-list actions
- `Wikipedia/Code/LegacyReadingListsDataSource.swift` · Core Data to SwiftUI models
- `Wikipedia/Code/ReadingListsController.swift` · reading-list sync and limits
- `Wikipedia/Code/SavedArticlesFetcher.swift` · offline downloads
- `WMFComponents/Sources/WMFComponents/Components/Saved/` · Saved views and view models
