---
title: Search Module
sub: Search topics and news as you type, with recent-search chips; opened from the top app bar's search icon.
card_title: Search
card: Instant search, with recent queries
screenshots:
- file: shots/search/01_results.jpg
  caption: 'Results as you type: matching topics, then articles'
- file: shots/search/02_empty.jpg
  caption: Search opens with the keyboard up and recent searches
---

## What it does {#what}

Opened from the search icon in the top app bar (`navigator.navigate(SearchNavKey)`), not a bottom
tab. The result state is gated two ways before a query ever runs a search: `SearchNotReady` while
the full-text-search table hasn't been populated yet (fewer than 1 indexed item), then
`EmptyQuery` while the typed query is under 2 characters — only past both does typing actually
search topics and news live, one `FullTextSearch` query per keystroke via
`GetSearchContentsUseCase`. A separate `RecentSearchQueriesUiState` lists up to the most recent
searches as tappable chips while the query box is otherwise empty; explicitly triggering a search
(the IME's search action, not just typing) saves it to that list, and a trash icon clears the
whole history.

## Logic · class diagram {#classes}

Two sibling states again, like Topic's header/news split — here it's the live results against the
recent-query history.

```mermaid
classDiagram
  direction LR
  class SearchScreen { <<page>> }
  class SearchViewModel {
    <<view-model>>
    searchQuery · searchResultUiState · recentSearchQueriesUiState
    onSearchQueryChanged(query)
    onSearchTriggered(query)
    clearRecentSearches()
    setNewsResourceBookmarked(newsResourceId, isChecked)
    followTopic(followedTopicId, followed)
  }
  class SearchResultUiState {
    <<state>>
    LoadFailed
  }
  class RecentSearchQueriesUiState { <<state>> }
  class GetSearchContentsUseCase { <<service>> }
  class SearchContentsRepository {
    <<service>>
    getSearchContentsCount()
  }
  class RecentSearchRepository {
    <<service>>
    insertOrReplaceRecentSearch() · clearRecentSearches()
  }
  class UserDataRepository { <<service>> }
  SearchScreen --> SearchViewModel : viewModel
  SearchViewModel --> SearchResultUiState : searchResultUiState
  SearchViewModel --> RecentSearchQueriesUiState : recentSearchQueriesUiState
  SearchViewModel ..> SearchContentsRepository : getSearchContentsCount()
  SearchViewModel ..> GetSearchContentsUseCase : invoke(query)
  SearchViewModel ..> RecentSearchRepository : insertOrReplaceRecentSearch()
  SearchViewModel ..> UserDataRepository : setNewsResourceBookmarked() · setTopicIdFollowed()
```

- `──▷` holds
- `┄┄▷` uses

## … · state machine {#result-state}

`SearchResultUiState` only ever reaches `Success`/`LoadFailed` once the FTS table is populated
*and* the query clears the 2-character minimum.

```mermaid
stateDiagram-v2
  [*] --> Loading
  Loading --> SearchNotReady : FTS entity count < 1
  Loading --> EmptyQuery : FTS ready, query shorter than 2 chars
  EmptyQuery --> Success : query reaches 2+ chars, search returns
  EmptyQuery --> LoadFailed : search throws
  Success --> EmptyQuery : query cleared back below 2 chars
```

## Screen · widget composition {#widgets}

Recent-search chips show only while there's no live result to display yet.

```mermaid
classDiagram
  direction TB
  class SearchScreen { <<page>> }
  class SearchNotReadyBody { <<widget>> }
  class RecentSearchQueriesUiState { <<state>> }
  class UserSearchResult { <<model>> }
  SearchScreen *-- SearchNotReadyBody : SearchNotReady
  SearchScreen --> RecentSearchQueriesUiState : recent-search chips, EmptyQuery
  SearchScreen --> UserSearchResult : Success topics + news
```

- `◆──` contains
- `──▷` reads model

## Type a query, then search it · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Screen as SearchScreen
  participant VM as SearchViewModel
  participant SearchUse as GetSearchContentsUseCase
  participant Recent as RecentSearchRepository
  User->>Screen: type in the search box
  Screen->>VM: onSearchQueryChanged(query)
  VM->>VM: searchQuery saved in SavedStateHandle
  alt query 2+ chars and FTS ready
    VM->>SearchUse: invoke(query)
    SearchUse-->>VM: searchResultUiState = Success(topics, news)
    VM-->>Screen: results render live, per keystroke
  end
  User->>Screen: tap the IME search action
  Screen->>VM: onSearchTriggered(query)
  VM->>Recent: insertOrReplaceRecentSearch(query)
  Note over Screen: query reappears as a recent-search chip next time the box is empty
```

## Key files {#files}

- `feature/search/impl/.../SearchScreen.kt` · search box, recent chips, results
- `feature/search/impl/.../SearchViewModel.kt` · query state, `SearchResultUiState`
- `feature/search/impl/.../SearchResultUiState.kt` · the result state machine
- `feature/search/impl/.../RecentSearchQueriesUiState.kt` · recent-search chip state
- `feature/search/impl/.../navigation/SearchEntryProvider.kt` · wires the nav key to the screen
- `feature/search/api/.../navigation/SearchNavKey.kt` · the nav key, opened from the top app bar
