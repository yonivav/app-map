---
title: Search Module
sub: The Search tab — recent searches and reading history until you type, then live results 200 ms after you stop, in any of your languages.
card_title: Search
card: Live article search with recent searches
screenshots:
- file: shots/search/01_tab.jpg
  caption: The Search tab with reading history
- file: shots/search/02_results.jpg
  caption: Results for each preferred language
---

## What it does {#what}

`SearchViewController` is the root of the Search tab (the app can be set to open on it). Before you type it shows your reading history below the search bar, with a clear-all button. Focusing the bar presents a `UISearchController` whose results controller is `SearchResultsViewController`: with an empty field it lists recent search terms, and as soon as there is non-blank text it waits 200 ms after the last keystroke (cancelling the previous wait), then searches. A language bar above the results switches the search to another of your preferred wikis and searches again. `SearchResultsLoader` runs the query through `WMFSearchFetcher` against that wiki; a running search is cancelled whenever a new one starts. Results are rendered by the SwiftUI `WMFSearchResultsView`; tapping one saves the term to recent searches and pushes the article. For readers enrolled in the semantic-search experiment, an entry point under the results opens a sheet of passage matches, and the chosen article scrolls to the highlighted passage.

## Logic · class diagram {#classes}

The tab controller owns the UIKit search controller; the results controller does the searching and owns the SwiftUI model.

```mermaid
classDiagram
  direction LR
  class SearchViewController {
    <<page>>
    searchResultsVC
    makeSearchBarBecomeFirstResponder()
    embedHistoryIfNeeded()
    deleteAll()
  }
  class SearchResultsViewController {
    <<page>>
    searchTerm · siteURL
    updateSearchResults()
    search()
    resetSearchResults()
    saveLastSearch()
    reloadRecentSearches()
  }
  class SearchResultsLoader {
    <<loader>>
    fetchResults()
  }
  class WMFSearchFetcher { <<search API>> }
  class WMFSearchResultsViewModel {
    <<view-model>>
    reset()
    hideSemanticSearchEntryPoint()
  }
  class SearchLanguagesBarViewController {
    <<widget>>
    selectedSearchContentLanguageCode
  }
  class SemanticSearchResultsCoordinator { <<coordinator>> }
  SearchViewController --> SearchResultsViewController : searchResultsVC
  SearchResultsViewController --> SearchResultsLoader : resultsLoader
  SearchResultsLoader ..> WMFSearchFetcher : searches the wiki
  SearchResultsViewController --> WMFSearchResultsViewModel : resultsViewModel
  SearchResultsViewController *-- SearchLanguagesBarViewController
  SearchViewController ..> SemanticSearchResultsCoordinator : semantic search sheet
```

- `──▷` holds
- `◆──` contains
- `┄┄▷` uses

## Screen · view composition {#widgets}

```mermaid
classDiagram
  direction TB
  class SearchViewController { <<page>> }
  class SearchResultsViewController { <<results>> }
  class SearchLanguagesBarViewController { <<language bar>> }
  class WMFSearchResultsView { <<SwiftUI>> }
  class WMFSearchResultsViewModel { <<view-model>> }
  SearchViewController *-- SearchResultsViewController : search controller results
  SearchResultsViewController *-- SearchLanguagesBarViewController
  SearchResultsViewController *-- WMFSearchResultsView
  WMFSearchResultsView --> WMFSearchResultsViewModel
```

- `◆──` contains
- `──▷` reads model

## Type a query · sequence {#sequence}

Each keystroke restarts a 200 ms wait; only the last one searches.

```mermaid
sequenceDiagram
  actor User
  participant Results as SearchResultsViewController
  participant Loader as SearchResultsLoader
  participant Fetcher as WMFSearchFetcher
  participant Model as WMFSearchResultsViewModel
  User->>Results: types "Ada Lov"
  Results->>Results: updateSearchResults(), cancels the last wait
  Note over Results: waits 200 ms with no new keystroke
  Results->>Results: search()
  Results->>Results: resetSearchResults(), cancels running fetches
  Results->>Loader: fetchResults()
  Loader->>Fetcher: searches the wiki
  Fetcher-->>Loader: titles, descriptions, thumbnails
  Loader-->>Results: outcome
  Results->>Model: shows the results
  User->>Results: tap Ada Lovelace
  Results->>Results: saveLastSearch(), pushes the article
```

## Key files {#files}

- `Wikipedia/Code/SearchViewController.swift` · Search tab, history, semantic search
- `Wikipedia/Code/SearchResultsViewController.swift` · debounced search and recent searches
- `Wikipedia/Code/SearchResultsLoader.swift` · runs a search
- `Wikipedia/Code/WMFSearchFetcher.m` · search API calls
- `Wikipedia/Code/SearchLanguagesBarViewController.swift` · language switcher
- `WMFComponents/Sources/WMFComponents/Components/Search/` · SwiftUI results and recent searches
