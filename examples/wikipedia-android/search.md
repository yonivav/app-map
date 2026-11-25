---
title: Search Module
sub: The Search tab's reading history and the search screen — recent searches, then prefix and full-text results 200 ms after you stop typing, mixed with matches from your tabs, history and reading lists.
card_title: Search
card: History, recent searches and live results
screenshots:
- file: shots/search/01_history.jpg
  caption: 'The Search tab: reading history and the search card'
- file: shots/search/02_recent.jpg
  caption: The search screen before typing
- file: shots/search/03_results.jpg
  caption: Results 200 ms after typing stops
---

## What it does {#what}

The Search tab is `HistoryFragment`: your reading history grouped by day, with a filter, multi-select to delete, and a search card at the top. Tapping the card (or the tab again) opens `SearchActivity` with `SearchFragment`, which shows one of two panels: `RecentSearchesFragment` (recent queries from Room, plus your languages) while the box is empty, and `SearchResultsFragment` as soon as there is text. Each keystroke updates the search term in `SearchResultsViewModel`, whose results flow is debounced by 200 ms and combined with the selected language, so only the last term is searched; changing the language chip re-runs it. `StandardSearchRepository` first adds up to one match each from your open tabs, your history and your reading lists (for terms of 2 or more characters), then a prefix search, and fills the page with a full-text search when there are fewer results than the batch size; results are paged with Paging 3. Tapping a result saves the query to recent searches and opens the article. Readers in the semantic-search test also get an entry to passage results.

## Logic · class diagram {#classes}

A fragment that swaps two panels, over a view model whose single flow does the debouncing.

```mermaid
classDiagram
  direction LR
  class HistoryFragment {
    <<page>>
    onPageClick()
  }
  class HistoryViewModel { <<view-model>> }
  class SearchActivity { <<activity>> }
  class SearchFragment {
    <<page>>
    startSearch()
    showPanel()
  }
  class RecentSearchesFragment { <<panel>> }
  class SearchResultsFragment {
    <<panel>>
    startSearch()
  }
  class SearchResultsViewModel {
    <<view-model>>
    searchResultsFlow
    updateSearchTerm()
    updateLanguageCode()
    refreshSearchResults()
  }
  class StandardSearchRepository {
    <<repository>>
    search()
  }
  class SearchResult {
    <<data>>
    pageTitle · type · snippet
  }
  class ServiceFactory {
    <<network>>
    get()
  }
  HistoryFragment --> HistoryViewModel
  HistoryFragment ..> SearchActivity : search card
  SearchActivity *-- SearchFragment
  SearchFragment *-- RecentSearchesFragment : empty box
  SearchFragment *-- SearchResultsFragment : with text
  SearchResultsFragment --> SearchResultsViewModel
  SearchResultsViewModel ..> StandardSearchRepository : search()
  StandardSearchRepository ..> ServiceFactory : prefix and full-text search
  StandardSearchRepository ..> SearchResult : builds
```

- `──▷` holds
- `◆──` contains
- `┄┄▷` uses · opens

## Screen · composition {#widgets}

```mermaid
classDiagram
  direction TB
  class SearchResultsFragment { <<panel>> }
  class SearchResultsScreen { <<composable>> }
  class SearchResultPageItem { <<composable>> }
  class NoSearchResults { <<composable>> }
  SearchResultsFragment *-- SearchResultsScreen
  SearchResultsScreen *-- SearchResultPageItem
  SearchResultsScreen *-- NoSearchResults
```

- `◆──` contains

## Type a query · sequence {#sequence}

The view model never searches on a keystroke: the debounced flow does, once typing pauses.

```mermaid
sequenceDiagram
  actor User
  participant Search as SearchFragment
  participant Results as SearchResultsFragment
  participant Model as SearchResultsViewModel
  participant Repo as StandardSearchRepository
  participant Api as ServiceFactory
  User->>Search: types "Ada Lov"
  Search->>Search: showPanel() results
  Search->>Results: startSearch()
  Results->>Model: updateSearchTerm()
  Note over Model: debounce 200 ms, then the latest term only
  Model->>Repo: search()
  Repo->>Repo: one match each from tabs, history, reading lists
  Repo->>Api: prefix search, then full text if short
  Api-->>Repo: pages
  Repo-->>Model: StandardSearchResults
  Model-->>Results: paged results
  User->>Results: tap Ada Lovelace
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/history/` · Search tab: reading history
- `app/src/main/java/org/wikipedia/search/SearchFragment.kt` · search screen and panels
- `app/src/main/java/org/wikipedia/search/SearchResultsViewModel.kt` · debounced, paged results
- `app/src/main/java/org/wikipedia/search/StandardSearchRepository.kt` · local matches, prefix and full-text search
- `app/src/main/java/org/wikipedia/search/RecentSearchesFragment.kt` · recent searches
- `app/src/main/java/org/wikipedia/search/SearchResultsScreen.kt` · results in Compose
