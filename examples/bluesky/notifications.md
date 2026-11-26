---
title: Notifications Module
sub: Grouped notifications in four tabs — All, People I follow, Conversations, Followers — with unread tracking and a refresh pill.
card_title: Notifications
card: Grouped notifications, four tabs, unread state
---

## What it does {#what}

`NotificationsScreen` renders `NotificationsScreenInner`: a header, tab pills and a pager with four feeds of the server's grouped notifications — **All**, **People I follow**, **Conversations** and **Followers**. Each tab's `PageList` reads `useGroupedNotificationsQuery` for its feed: pages of `getGroupedNotifications`, hydrated against each page's related posts and profiles, moderated, and never refreshed on their own — the screen decides when. To know whether a tab has something new without loading it, it peeks at just the newest group (`limit: 1`) and shows a refresh pill. Refreshing **All** brings the other tabs along and the other way round; tabs refreshed while out of view are marked stale and reload when opened. What's been seen is tracked per session (`useSessionSeenAt`): loading **All** marks its items as seen and calls `updateSeen` on the server through `useUnreadNotificationsApi`, which also drives the badge on the tab bar. Each row is a `NotificationItem` that groups the actors behind a like, repost, follow, reply, mention or quote.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class NotificationsScreenInner {
    <<screen>>
  }
  class PageList { <<component>> }
  class GroupedNotificationsFeed {
    <<type>>
  }
  class useGroupedNotificationsQuery { <<hook>> }
  class useSessionSeenAt {
    <<hook>>
    seenAt · onFirstLoad · refresh
  }
  class useUnreadNotificationsApi {
    <<hook>>
  }
  NotificationsScreenInner *-- PageList : one per tab
  PageList --> GroupedNotificationsFeed : feed
  PageList ..> useGroupedNotificationsQuery : pages of groups
  NotificationsScreenInner ..> useSessionSeenAt : seenAt
  NotificationsScreenInner ..> useUnreadNotificationsApi : markAllRead
```

- `◆──` contains
- `──▷` holds
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class NotificationsScreen { <<screen>> }
  class NotificationsScreenInner { <<screen>> }
  class TabPills { <<component>> }
  class PageList { <<component>> }
  class NotificationItem {
    <<component>>
  }
  class RefreshPill { <<component>> }
  NotificationsScreen *-- NotificationsScreenInner
  NotificationsScreenInner *-- TabPills : All, People I follow, Conversations, Followers
  NotificationsScreenInner *-- PageList
  PageList *-- NotificationItem
  PageList *-- RefreshPill : newer groups available
```

- `◆──` contains

## Open notifications · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Screen as NotificationsScreenInner
  participant List as PageList
  participant Query as useGroupedNotificationsQuery
  participant Unread as useUnreadNotificationsApi
  User->>Screen: opens the Notifications tab
  Screen->>List: All
  List->>Query: getGroupedNotifications
  Query-->>List: hydrated, moderated groups
  Screen->>Unread: marks everything up to seenAt as read
  Unread-->>User: tab badge cleared
  Note over List: later, a peek at the newest group shows a refresh pill
  User->>List: taps the pill
  List->>Query: refresh, other tabs marked stale
```

## Key files {#files}

- `src/screens/Notifications/index.tsx` · screen, tabs, refresh and seen logic
- `src/screens/Notifications/components/` · page list, tab pills, notification rows
- `src/state/queries/notifications/grouped/` · grouped query, hydration, moderation
- `src/state/queries/notifications/unread.tsx` · unread count and mark-as-read
