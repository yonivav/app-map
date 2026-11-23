---
title: Bookmarks Module
sub: 'The saved tab: every bookmarked article in the same staggered grid as For You, with an undo snackbar.'
card_title: Bookmarks
card: Saved articles, with undo
screenshots:
- file: shots/bookmarks/01_saved.jpg
  caption: A saved article
- file: shots/bookmarks/02_empty.jpg
  caption: Nothing saved yet
---

## What it does {#what}

The grid lists only news resources you've bookmarked (`observeAllBookmarked()`), reusing the same
`newsFeed()` composable as the For You module. Un-bookmarking a card doesn't remove it from the
list right away: the view-model flips `shouldDisplayUndoBookmark` and remembers the id, the screen
shows a snackbar with an **Undo** action, and only once the snackbar is dismissed without being
undone does `clearUndoState()` run — the underlying `setNewsResourceBookmarked(id, false)` already
happened, so the list re-filters itself out on the next `observeAllBookmarked()` emission. An empty
list shows a dedicated illustration and caption instead of a blank grid.

## Logic · class diagram {#classes}

No onboarding here — one repository pair feeds one state, plus two plain `mutableStateOf` fields
for the undo snackbar.

```mermaid
classDiagram
  direction LR
  class BookmarksScreen { <<page>> }
  class BookmarksViewModel {
    <<view-model>>
    feedUiState · shouldDisplayUndoBookmark
    removeFromSavedResources(newsResourceId)
    setNewsResourceViewed(newsResourceId, viewed)
    undoBookmarkRemoval()
    clearUndoState()
  }
  class NewsFeedUiState { <<state>> }
  class UserNewsResourceRepository {
    <<service>>
    observeAllBookmarked()
  }
  class UserDataRepository {
    <<service>>
    setNewsResourceBookmarked()
  }
  BookmarksScreen --> BookmarksViewModel : viewModel
  BookmarksViewModel --> NewsFeedUiState : feedUiState
  BookmarksViewModel ..> UserNewsResourceRepository : observeAllBookmarked()
  BookmarksViewModel ..> UserDataRepository : setNewsResourceBookmarked()
```

- `──▷` holds
- `┄┄▷` uses

## Screen · widget composition {#widgets}

A staggered grid of the same cards as For You, or one `EmptyState` in their place.

```mermaid
classDiagram
  direction TB
  class BookmarksScreen { <<page>> }
  class EmptyState { <<widget>> }
  class UserNewsResource { <<model>> }
  BookmarksScreen *-- EmptyState : when the feed is empty
  BookmarksScreen --> UserNewsResource : newsFeed items
```

- `◆──` contains
- `──▷` reads model

## Un-bookmark, then undo · sequence {#sequence}

The snackbar is the only thing standing between "removed" and "still there."

```mermaid
sequenceDiagram
  actor User
  participant Screen as BookmarksScreen
  participant VM as BookmarksViewModel
  participant UserData as UserDataRepository
  User->>Screen: tap the bookmark toggle on a card
  Screen->>VM: removeFromSavedResources(newsResourceId)
  VM->>VM: shouldDisplayUndoBookmark = true
  VM->>UserData: setNewsResourceBookmarked(id, false)
  VM-->>Screen: feedUiState re-filters the card out
  Screen->>Screen: shows the undo snackbar
  alt user taps Undo
    User->>Screen: tap Undo
    Screen->>VM: undoBookmarkRemoval()
    VM->>UserData: setNewsResourceBookmarked(id, true)
    VM->>VM: clearUndoState()
  else snackbar times out
    Screen->>VM: clearUndoState()
  end
```

## Key files {#files}

- `feature/bookmarks/impl/.../BookmarksScreen.kt` · the grid, undo snackbar, empty state
- `feature/bookmarks/impl/.../BookmarksViewModel.kt` · feed state + undo-bookmark bookkeeping
- `feature/bookmarks/impl/.../navigation/BookmarksEntryProvider.kt` · wires the nav key to the screen
- `feature/bookmarks/api/.../navigation/BookmarksNavKey.kt` · the top-level nav key
