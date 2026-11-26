---
title: Home Module
sub: The Home tab — a swipeable pager of your pinned feeds (Following, Discover, custom feeds and lists), each an infinite, cached list of posts.
card_title: Home
card: Pinned feeds in a pager, infinite post lists
---

## What it does {#what}

`HomeScreen` waits for your preferences and pinned feeds, then renders `HomeScreenReady`: a `Pager` with one page per pinned feed and a tab bar in the header, remembering the selected feed (`useSetSelectedFeed`). Each page is a `FeedPage` around `PostFeed`, which calls `usePostFeedQuery` with a feed descriptor — `following`, `feedgen|…`, `list|…`, `author|…`, `likes|…` or `posts|…`. The query turns the descriptor into a `FeedAPI`: `FollowingFeedAPI` (or `MergeFeedAPI` when merging is on, or `HomeFeedAPI` when an empty Following falls back to Discover), `CustomFeedAPI`, `ListFeedAPI`, `AuthorFeedAPI`, `LikesFeedAPI` or `PostListFeedAPI`. It fetches 30 posts per page, keeps the API instance in the page params so the next page uses the same cursor, and never goes stale on its own (`STALE.INFINITY`): new posts come from polling `peekLatest()` and a "new posts" pill, or a pull to refresh. Feed tuners remove duplicates and posts your preferences hide before rendering. `PostFeed` renders rows of `PostFeedItem` and mixes in interstitials — suggested follows, trending topics, the progress guide — plus empty and error states.

## Logic · class diagram {#classes}

One hook, many feed kinds: the descriptor picks the API; the query caches the pages.

```mermaid
classDiagram
  direction LR
  class HomeScreenReady {
    <<screen>>
    pinnedFeedInfos
  }
  class PostFeed {
    <<component>>
    feed · feedParams · pollInterval
  }
  class usePostFeedQuery {
    <<hook>>
    feedTuners · query
  }
  class FeedAPI {
    <<interface>>
    peekLatest()
    fetch()
  }
  class FollowingFeedAPI { <<feed API>> }
  class HomeFeedAPI { <<feed API>> }
  class CustomFeedAPI { <<feed API>> }
  class ListFeedAPI { <<feed API>> }
  class AuthorFeedAPI { <<feed API>> }
  class MergeFeedAPI { <<feed API>> }
  HomeScreenReady ..> PostFeed : one per pinned feed
  PostFeed ..> usePostFeedQuery : the feed's pages
  usePostFeedQuery --> FeedAPI : each page keeps its api and cursor
  FeedAPI <|.. FollowingFeedAPI
  FeedAPI <|.. HomeFeedAPI
  FeedAPI <|.. CustomFeedAPI
  FeedAPI <|.. ListFeedAPI
  FeedAPI <|.. AuthorFeedAPI
  FeedAPI <|.. MergeFeedAPI
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `┄┄▷|` implements

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class HomeScreenReady { <<screen>> }
  class HomeHeader { <<component>> }
  class Pager { <<component>> }
  class PostFeed { <<component>> }
  class PostFeedItem {
    <<component>>
    post · record · reason · moderation
  }
  class SuggestedFollows { <<interstitial>> }
  class FeedTrendingTopicsInterstitial { <<interstitial>> }
  class PostFeedErrorMessage { <<component>> }
  class FollowingEmptyState { <<component>> }
  HomeScreenReady *-- HomeHeader : feed tabs
  HomeScreenReady *-- Pager
  Pager *-- PostFeed : one page per feed
  PostFeed *-- PostFeedItem
  PostFeed *-- SuggestedFollows
  PostFeed *-- FeedTrendingTopicsInterstitial
  PostFeed *-- PostFeedErrorMessage
  HomeScreenReady *-- FollowingEmptyState
```

- `◆──` contains

## Scroll the Following feed · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Home as HomeScreenReady
  participant Feed as PostFeed
  participant Query as usePostFeedQuery
  participant Api as FollowingFeedAPI
  User->>Home: opens Home, Following selected
  Home->>Feed: feed = following
  Feed->>Query: asks for the feed's pages
  Query->>Api: fetch(), 30 posts, no cursor
  Api-->>Query: posts and a cursor
  Query-->>Feed: tuned slices, page 1
  User->>Feed: scrolls near the end
  Feed->>Query: fetchNextPage
  Query->>Api: fetch(), same API, next cursor
  Note over Query: cached — only polling or a refresh brings newer posts
  User->>Feed: pull to refresh
  Feed->>Query: refetch from the top
```

## Key files {#files}

- `src/view/screens/Home.tsx` · Home tab, pinned-feed pager
- `src/view/com/posts/PostFeed.tsx` · the post list and its interstitials
- `src/view/com/posts/PostFeedItem.tsx` · one post row
- `src/state/queries/post-feed.ts` · feed query, paging, API per descriptor
- `src/lib/api/feed/` · one `FeedAPI` per kind of feed
- `src/view/com/pager/` · the swipeable pager
