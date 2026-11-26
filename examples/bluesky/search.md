---
title: Search Module
sub: "The Search tab — Explore before you type, then autocomplete and five result tabs: Top, Latest, People, Feeds and Starter Packs."
card_title: Search
card: Explore, autocomplete, five result tabs
---

## What it does {#what}

`SearchScreen` is the Search tab's root and renders `SearchScreenShell`, the same shell that also serves profile search and hashtag pages. With an empty box it shows `Explore`: trending topics, trending videos, suggested accounts by interest, feed previews and starter packs. Typing shows autocomplete results for people (`useActorSearch`) and your search history, which is stored on the device; submitting runs the search and shows `SearchResults`, a pager with five tabs — **Top** and **Latest** posts (`useSearchPostsV2Query`), **People** (`useActorSearch`), **Feeds** (`usePopularFeedsSearch`) and **Starter Packs**. The People and Feeds tabs only appear when no post-only filter (such as a language) is set. An advanced-search dialog builds filters into the query (`from:`, `since:`, language), and a language admonition suggests one when the query's language is detected. Results are paged and cached like every other query.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class SearchScreen { <<screen>> }
  class SearchScreenShell {
    <<component>>
    queryParam · fixedParams · isExplore
  }
  class SearchScreenInner { <<component>> }
  class Explore { <<component>> }
  class SearchResults {
    <<component>>
    query · activeTab
  }
  class useSearchPostsV2Query { <<hook>> }
  class useActorSearch { <<hook>> }
  class usePopularFeedsSearch { <<hook>> }
  SearchScreen *-- SearchScreenShell
  SearchScreenShell *-- SearchScreenInner
  SearchScreenInner *-- Explore : empty query
  SearchScreenInner *-- SearchResults : a query
  SearchResults ..> useSearchPostsV2Query : Top, Latest
  SearchResults ..> useActorSearch : People
  SearchResults ..> usePopularFeedsSearch : Feeds
```

- `◆──` contains
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class SearchScreenShell { <<component>> }
  class SearchAutocompleteInput { <<component>> }
  class AutocompleteResults { <<component>> }
  class SearchHistory { <<component>> }
  class AdvancedSearchDialog { <<dialog>> }
  class SearchResults { <<component>> }
  class SearchScreenPostResults { <<tab>> }
  class SearchScreenUserResults { <<tab>> }
  class SearchScreenFeedsResults { <<tab>> }
  SearchScreenShell *-- SearchAutocompleteInput
  SearchScreenShell *-- AutocompleteResults : while typing
  SearchScreenShell *-- SearchHistory
  SearchScreenShell *-- AdvancedSearchDialog
  SearchScreenShell *-- SearchResults
  SearchResults *-- SearchScreenPostResults : Top, Latest
  SearchResults *-- SearchScreenUserResults : People
  SearchResults *-- SearchScreenFeedsResults : Feeds
```

- `◆──` contains

## Search for a topic · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Shell as SearchScreenShell
  participant Results as SearchResults
  participant Posts as useSearchPostsV2Query
  participant People as useActorSearch
  User->>Shell: opens Search
  Shell-->>User: Explore, trending and suggestions
  User->>Shell: types "react native"
  Shell->>People: autocomplete people
  User->>Shell: submits
  Shell->>Results: query
  Results->>Posts: Top tab
  Posts-->>Results: first page of posts
  User->>Results: swipes to People
  Results->>People: full people search
```

## Key files {#files}

- `src/screens/Search/Shell.tsx` · search shell, input, autocomplete, history
- `src/screens/Search/SearchResults.tsx` · the five result tabs
- `src/screens/Search/Explore.tsx` · Explore modules
- `src/screens/Search/modules/` · trending, suggested accounts, feed previews
- `src/state/queries/search-posts-v2.ts` · post search
- `src/state/queries/actor-search.ts` · people search
