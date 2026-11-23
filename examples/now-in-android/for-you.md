---
title: For You Module
sub: "The home feed: a one-time topic-picking onboarding, then a staggered grid of news from your followed topics."
card_title: For You
card: Topic onboarding + the staggered news feed
---

## What it does {#what}

The first time the app runs (`shouldHideOnboarding` is false in the saved `UserData`), the feed's
top item is a topic-picking grid: a 3-row horizontal `LazyHorizontalGrid` of every followable
topic, each a toggle button. **Done** only enables once at least one topic is followed
(`isDismissable`); tapping it calls `setShouldHideOnboarding(true)` and the onboarding item
disappears for good. Below it, a `LazyVerticalStaggeredGrid` lists news from the topics you
follow, each card toggle-able as bookmarked. A top loading wheel slides in while syncing or while
either the onboarding or the feed is still loading, and a deep-linked article (`linkedNewsResourceId`
on the nav key, or a notification's `DEEP_LINK_NEWS_RESOURCE_ID_KEY`) opens straight into a Chrome
custom tab and is marked viewed. On API 33+, the screen asks once for the notification permission
if it hasn't been denied before.

## Logic · class diagram {#classes}

The screen is pure Compose state fed by one view-model; onboarding and the feed are two
independent `StateFlow`s combined only for layout.

```mermaid
classDiagram
  direction LR
  class ForYouScreen { <<page>> }
  class ForYouViewModel {
    <<view-model>>
    onboardingUiState · feedState · isSyncing · deepLinkedNewsResource
    updateTopicSelection(topicId, isChecked)
    updateNewsResourceSaved(newsResourceId, isChecked)
    setNewsResourceViewed(newsResourceId, viewed)
    dismissOnboarding()
    onDeepLinkOpened(newsResourceId)
  }
  class OnboardingUiState {
    <<state>>
    Loading · LoadFailed · NotShown
  }
  class NewsFeedUiState {
    <<state>>
    Loading
  }
  class UserNewsResourceRepository { <<service>> }
  class UserDataRepository {
    <<service>>
    setTopicIdFollowed() · setShouldHideOnboarding()
  }
  class SyncManager { <<service>> }
  class GetFollowableTopicsUseCase { <<service>> }
  class ForYouNavKey {
    <<data>>
    linkedNewsResourceId
  }
  ForYouScreen --> ForYouViewModel : viewModel
  ForYouViewModel ..> UserNewsResourceRepository : observeAllForFollowedTopics()
  ForYouViewModel ..> UserDataRepository : setTopicIdFollowed() · setShouldHideOnboarding()
  ForYouViewModel ..> SyncManager : isSyncing
  ForYouViewModel ..> GetFollowableTopicsUseCase : invoke()
  ForYouViewModel --> OnboardingUiState : onboardingUiState
  ForYouViewModel --> NewsFeedUiState : feedState
  ForYouViewModel --> ForYouNavKey : key
```

- `──▷` holds
- `┄┄▷` uses

## … · state machine {#onboarding-state}

`OnboardingUiState` starts `Loading` until `userData` and the followable-topics list both arrive;
after that it never goes back to `Loading`.

```mermaid
stateDiagram-v2
  [*] --> Loading
  Loading --> Shown : shouldHideOnboarding is false
  Loading --> NotShown : shouldHideOnboarding is true
  Shown --> NotShown : Done tapped, isDismissable → setShouldHideOnboarding(true)
```

## Screen · widget composition {#widgets}

One scrollable grid holds both sections; the loading wheel and scrollbar float above it.

```mermaid
classDiagram
  direction TB
  class ForYouScreen { <<page>> }
  class TopicSelection { <<widget>> }
  class SingleTopicButton { <<widget>> }
  class TopicIcon { <<widget>> }
  class NiaButton { <<Done button>> }
  class NiaOverlayLoadingWheel { <<widget>> }
  class DraggableScrollbar { <<widget>> }
  class UserNewsResource { <<model>> }
  ForYouScreen *-- TopicSelection : onboarding section
  TopicSelection *-- SingleTopicButton
  SingleTopicButton *-- TopicIcon
  TopicSelection *-- NiaButton
  ForYouScreen *-- NiaOverlayLoadingWheel
  ForYouScreen *-- DraggableScrollbar
  ForYouScreen --> UserNewsResource : newsFeed items
```

- `◆──` contains
- `──▷` reads model

## Follow a topic, then open a deep-linked article · sequence {#sequence}

Both paths run through the same repositories; only the destination differs.

```mermaid
sequenceDiagram
  actor User
  participant Screen as ForYouScreen
  participant VM as ForYouViewModel
  participant UserData as UserDataRepository
  User->>Screen: tap a topic in onboarding
  Screen->>VM: updateTopicSelection(topicId, true)
  VM->>UserData: setTopicIdFollowed(topicId, true)
  UserData-->>VM: userData StateFlow emits
  VM-->>Screen: feedState recomputes with the new topic
  User->>Screen: tap Done
  Screen->>VM: dismissOnboarding()
  VM->>UserData: setShouldHideOnboarding(true)
  Note over Screen: onboarding item disappears from the grid
  User->>Screen: tap a notification for a followed topic
  Screen->>VM: onDeepLinkOpened(newsResourceId)
  VM->>UserData: setNewsResourceViewed(newsResourceId, true)
  VM-->>Screen: deepLinkedNewsResource emits the article
  Screen->>Screen: DeepLinkEffect opens a Chrome custom tab
```

## Key files {#files}

- `feature/foryou/impl/.../ForYouScreen.kt` · the grid, onboarding section, deep-link effect
- `feature/foryou/impl/.../ForYouViewModel.kt` · onboarding + feed state, topic/bookmark toggles
- `feature/foryou/impl/.../OnboardingUiState.kt` · the onboarding state machine
- `feature/foryou/impl/.../navigation/ForYouEntryProvider.kt` · wires the nav key to the screen
- `feature/foryou/api/.../navigation/ForYouNavKey.kt` · the top-level nav key, carries a deep link id
- `core/ui/.../NewsFeed.kt` · `NewsFeedUiState` and the shared `newsFeed()` grid items
