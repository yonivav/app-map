---
title: Post Thread Module
sub: A post with its parents above and replies below, threaded or linear, sorted three ways, with hidden and muted replies kept apart.
card_title: Post thread
card: Parents, anchor post, replies
---

## What it does {#what}

Tapping a post anywhere pushes `PostThread` with its URI. `usePostThread` calls `getPostThreadV2` for that anchor with the chosen `sort` and `view` and a reply depth that depends on the view: 10 levels deep in the **linear** view, 4 in the **threaded** tree (6 on desktop web). A second query, `getPostThreadOtherV2`, fetches the replies hidden by the author or by your moderation settings, shown only when you ask for them. The response is sorted and annotated into thread items: parents above the anchor, the anchor itself (`ThreadItemAnchor`), then replies as `ThreadItemPost` (linear) or `ThreadItemTreePost` (threaded), with "read more" rows where a branch goes deeper, and skeletons while loading. The header menu switches between **Linear** and **Threaded** and sorts by **Top**, **Oldest** or **Newest** replies first; a change is treated like a cold load, keeping the anchor in place while parents load. Signed out, posts from accounts that hide from logged-out viewers become placeholders. Replying opens the composer; a successful reply is inserted into the thread right away (`insertReplies`), before the server echoes it back.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class PostThread {
    <<screen>>
    uri
    thread
    optimisticOnPostReply
  }
  class usePostThread {
    <<hook>>
    thread · threadgate
    hasOtherThreadItems · otherItemsVisible
  }
  class PostThreadParams { <<data>> }
  class ThreadItem {
    <<data>>
  }
  class useComposerControls {
    <<hook>>
  }
  PostThread ..> usePostThread : anchor, view, sort
  usePostThread --> PostThreadParams : query key
  usePostThread o-- ThreadItem : sorted, annotated items
  PostThread ..> useComposerControls : reply
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class PostThread { <<screen>> }
  class HeaderDropdown { <<menu>> }
  class ThreadItemAnchor { <<component>> }
  class ThreadItemPost { <<component>> }
  class ThreadItemTreePost { <<component>> }
  class ThreadItemReadMore { <<component>> }
  class ThreadItemShowOtherReplies { <<component>> }
  class ThreadItemPostSkeleton { <<component>> }
  class ThreadComposePrompt { <<component>> }
  PostThread *-- HeaderDropdown : view and sort
  PostThread *-- ThreadItemAnchor
  PostThread *-- ThreadItemPost : linear view
  PostThread *-- ThreadItemTreePost : threaded view
  PostThread *-- ThreadItemReadMore
  PostThread *-- ThreadItemShowOtherReplies : hidden replies
  PostThread *-- ThreadItemPostSkeleton
  PostThread *-- ThreadComposePrompt
```

- `◆──` contains

## Open a thread, reply · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Thread as PostThread
  participant Query as usePostThread
  participant Composer as useComposerControls
  User->>Thread: taps a post
  Thread->>Query: asks for the thread of the anchor
  Query->>Query: getPostThreadV2, sort and view, depth 4 or 10
  Query-->>Thread: parents, anchor, replies
  Thread-->>User: anchor in place, parents above
  User->>Thread: Threaded, Oldest replies first
  Thread->>Query: setView, setSort, cold load
  User->>Thread: Reply
  Thread->>Composer: opens the composer as a reply
  Composer-->>Thread: posted
  Thread->>Query: insertReplies, shown at once
```

## Key files {#files}

- `src/screens/PostThread/index.tsx` · thread screen and its list
- `src/screens/PostThread/components/` · anchor, posts, tree, read more, header menu
- `src/state/queries/usePostThread/` · thread queries, sorting, optimistic replies
