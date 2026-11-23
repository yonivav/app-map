---
title: Interests Module
sub: Every topic you can follow, alphabetically, with a follow toggle; tapping one opens its Topic detail.
card_title: Interests
card: All topics, with a follow toggle
screenshots:
- file: shots/interests/01_topics.jpg
  caption: Every topic, with a follow toggle
---

## What it does {#what}

A single tab lists every topic (`GetFollowableTopicsUseCase`, sorted by name) with a toggle for
whether you follow it; toggling calls `setTopicIdFollowed` straight through to
`UserDataRepository`, no local state. Tapping a topic name (not the toggle) opens the Topic
module. On a wide screen, the Interests list is the **list pane** of a two-pane layout
(`ListDetailSceneStrategy`) — the Topic module then renders as its **detail pane** alongside it,
and before any topic is picked the detail pane shows `InterestsDetailPlaceholder`, a plain "pick a
topic" card, instead of being empty. On a narrow screen there's no detail pane: tapping a topic
pushes it onto the current tab's back stack instead.

## Logic · class diagram {#classes}

The selected topic id (only meaningful for the two-pane layout) rides in `SavedStateHandle`
alongside the nav key's own `initialTopicId`.

```mermaid
classDiagram
  direction LR
  class InterestsScreen { <<page>> }
  class InterestsViewModel {
    <<view-model>>
    uiState
    followTopic(followedTopicId, followed)
    onTopicClick(topicId)
  }
  class InterestsUiState {
    <<state>>
    Loading · Empty
  }
  class GetFollowableTopicsUseCase { <<service>> }
  class UserDataRepository {
    <<service>>
    setTopicIdFollowed()
  }
  class InterestsNavKey {
    <<data>>
    initialTopicId
  }
  InterestsScreen --> InterestsViewModel : viewModel
  InterestsViewModel --> InterestsUiState : uiState
  InterestsViewModel ..> GetFollowableTopicsUseCase : invoke(sortBy)
  InterestsViewModel ..> UserDataRepository : setTopicIdFollowed()
  InterestsViewModel --> InterestsNavKey : key
```

- `──▷` holds
- `┄┄▷` uses

## Screen · widget composition {#widgets}

`TabContent` is the same list row builder the Topic module reuses for "topics you might also
follow."

```mermaid
classDiagram
  direction TB
  class InterestsScreen { <<page>> }
  class TopicsTabContent { <<widget>> }
  class InterestsDetailPlaceholder { <<wide-screen detail pane>> }
  class FollowableTopic { <<model>> }
  InterestsScreen *-- TopicsTabContent : the topic list
  TopicsTabContent --> FollowableTopic : reads
```

- `◆──` contains
- `──▷` reads model

## Follow a topic, then open it · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Screen as InterestsScreen
  participant VM as InterestsViewModel
  participant UserData as UserDataRepository
  participant Nav as Navigator
  User->>Screen: tap a topic's follow toggle
  Screen->>VM: followTopic(topicId, true)
  VM->>UserData: setTopicIdFollowed(topicId, true)
  VM-->>Screen: uiState re-emits with the topic followed
  User->>Screen: tap the topic's name
  Screen->>VM: onTopicClick(topicId)
  VM->>VM: selectedTopicId saved in SavedStateHandle
  Screen->>Nav: navigate(key), a TopicNavKey holding topicId
  Note over Screen: wide screen → Topic renders in the detail pane · narrow → pushes onto the tab's stack
```

## Key files {#files}

- `feature/interests/impl/.../InterestsScreen.kt` · the topic list, list-detail wiring
- `feature/interests/impl/.../InterestsViewModel.kt` · `InterestsUiState`, follow/select actions
- `feature/interests/impl/.../TabContent.kt` · the shared topic-row list, reused by Topic
- `feature/interests/impl/.../InterestsDetailPlaceholder.kt` · the wide-screen empty detail pane
- `feature/interests/impl/.../navigation/InterestsEntryProvider.kt` · the list-pane nav wiring
- `feature/interests/api/.../navigation/InterestsNavKey.kt` · the top-level nav key
