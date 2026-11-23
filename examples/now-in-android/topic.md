---
title: Topic Module
sub: 'One topic''s detail: its header with a follow button, and the news written about it.'
card_title: Topic
card: A topic's header, follow button and news
screenshots:
- file: shots/topic/01_header.jpg
  caption: A topic's header and its news
- file: shots/topic/02_news.jpg
  caption: The topic's news, scrolled
---

## What it does {#what}

Reached from For You, Interests or Search with just a topic id (`TopicNavKey(id)`), the screen
combines two independent streams into two separate sealed states: `TopicUiState` (the topic's
name, description, image and whether you follow it) and `NewsUiState` (the news written about it,
each with its own bookmark state) — each can be `Loading`, `Error` or `Success` on its own clock,
so the header can appear before the news list finishes loading. `TopicToolbar` shows a back
arrow and, once the topic has loaded, a follow toggle right there in the app bar; toggling it
calls straight through to `UserDataRepository`, same as everywhere else in the app.

## Logic · class diagram {#classes}

Two sibling `combine()` flows, each wrapped in `asResult()` so loading/error show up as states
instead of being handled ad hoc.

```mermaid
classDiagram
  direction LR
  class TopicScreen { <<page>> }
  class TopicViewModel {
    <<view-model>>
    topicUiState · newsUiState · topicId
    followTopicToggle(followed)
    bookmarkNews(newsResourceId, bookmarked)
    setNewsResourceViewed(newsResourceId, viewed)
  }
  class TopicUiState {
    <<state>>
    Error · Loading
  }
  class NewsUiState {
    <<state>>
    Error · Loading
  }
  class TopicsRepository { <<service>> }
  class UserNewsResourceRepository { <<service>> }
  class UserDataRepository {
    <<service>>
    setTopicIdFollowed()
  }
  class TopicNavKey {
    <<data>>
    id
  }
  TopicScreen --> TopicViewModel : viewModel
  TopicViewModel --> TopicUiState : topicUiState
  TopicViewModel --> NewsUiState : newsUiState
  TopicViewModel ..> TopicsRepository : getTopic(id)
  TopicViewModel ..> UserNewsResourceRepository : observeAll(query)
  TopicViewModel ..> UserDataRepository : setTopicIdFollowed() · setNewsResourceBookmarked()
  TopicViewModel --> TopicNavKey : topicId
```

- `──▷` holds
- `┄┄▷` uses

## Screen · widget composition {#widgets}

The toolbar, header and news list are three independent sections the same list; a header or news
item is only drawn once its own state is `Success`.

```mermaid
classDiagram
  direction TB
  class TopicScreen { <<page>> }
  class TopicToolbar { <<back + follow toggle>> }
  class TopicHeader { <<widget>> }
  class FollowableTopic { <<model>> }
  class UserNewsResource { <<model>> }
  TopicScreen *-- TopicToolbar
  TopicScreen *-- TopicHeader : topicUiState.Success
  TopicHeader --> FollowableTopic : reads
  TopicScreen --> UserNewsResource : newsUiState.Success items
```

- `◆──` contains
- `──▷` reads model

## Open a topic and follow it · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Nav as Navigator
  participant Screen as TopicScreen
  participant VM as TopicViewModel
  participant Topics as TopicsRepository
  participant UserData as UserDataRepository
  User->>Nav: navigate(key), a TopicNavKey holding topicId
  Nav-->>Screen: the TopicNavKey enters the back stack
  Screen->>VM: hiltViewModel creates it via Factory.create
  VM->>Topics: getTopic(topicId)
  Topics-->>VM: topicUiState = Success(followableTopic)
  VM-->>Screen: TopicHeader + follow toggle render
  User->>Screen: tap the follow toggle
  Screen->>VM: followTopicToggle(true)
  VM->>UserData: setTopicIdFollowed(topicId, true)
  UserData-->>VM: topicUiState re-emits, isFollowed = true
```

## Key files {#files}

- `feature/topic/impl/.../TopicScreen.kt` · toolbar, header, news list
- `feature/topic/impl/.../TopicViewModel.kt` · `TopicUiState`, `NewsUiState`, follow/bookmark actions
- `feature/topic/impl/.../navigation/TopicEntryProvider.kt` · wires the nav key to the screen
- `feature/topic/api/.../navigation/TopicNavKey.kt` · the nav key and `navigateToTopic()`
