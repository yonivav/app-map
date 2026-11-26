---
title: Profile Module
sub: A profile — header with follow and edit, and a pager of up to nine tabs, from Posts and Replies to Feeds, Lists and Starter Packs.
card_title: Profile
card: Header and tabs of a profile
---

## What it does {#what}

Profiles open by handle or DID: `ProfileScreenInner` resolves the handle to a DID (`useResolveDidQuery`), loads the profile (`useProfileQuery`), and renders `ProfileScreenLoaded` once both are there; a placeholder from a feed item can show at once while the full profile loads. Content that moderation hides is wrapped in a `ScreenHider` you can choose to look past. `ProfileHeader` shows the banner, avatar, names, bio, counts, and **Follow**, **Edit profile** or **Subscribe** for labelers. Below it, `PagerWithHeader` holds only the tabs that apply: **Labels** and **Lists** for a labeler, then **Posts**, **Replies**, **Media**, **Videos**, **Likes** (your own profile), **Feeds**, **Starter Packs** and **Lists** when the account has any. The post tabs are `ProfileFeedSection`s around the same `PostFeed` as Home, with an `author|…` or `likes|…` feed descriptor, so they page and cache the same way. A floating button opens the composer, prefilled with a mention when you're on someone else's profile.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class ProfileScreenInner {
    <<screen>>
    route
  }
  class ProfileScreenLoaded {
    <<component>>
  }
  class useResolveDidQuery { <<hook>> }
  class useProfileQuery { <<hook>> }
  class ProfileFeedSection { <<component>> }
  class PostFeed { <<component>> }
  class usePostFeedQuery { <<hook>> }
  ProfileScreenInner ..> useResolveDidQuery : handle to DID
  ProfileScreenInner ..> useProfileQuery : the profile
  ProfileScreenInner *-- ProfileScreenLoaded
  ProfileScreenLoaded *-- ProfileFeedSection : Posts, Replies, Media, Videos, Likes
  ProfileFeedSection *-- PostFeed
  PostFeed ..> usePostFeedQuery : author or likes feed
```

- `◆──` contains
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class ProfileScreenLoaded { <<component>> }
  class ScreenHider { <<moderation>> }
  class PagerWithHeader { <<component>> }
  class ProfileHeader { <<component>> }
  class ProfileFeedSection { <<tab>> }
  class ProfileFeedgens { <<tab>> }
  class ProfileStarterPacks { <<tab>> }
  class ProfileLists { <<tab>> }
  class ProfileLabelsSection { <<tab>> }
  ProfileScreenLoaded *-- ScreenHider
  ProfileScreenLoaded *-- PagerWithHeader
  PagerWithHeader *-- ProfileHeader
  PagerWithHeader *-- ProfileFeedSection
  PagerWithHeader *-- ProfileFeedgens : Feeds
  PagerWithHeader *-- ProfileStarterPacks : Starter Packs
  PagerWithHeader *-- ProfileLists : Lists
  PagerWithHeader *-- ProfileLabelsSection : a labeler's labels
```

- `◆──` contains

## Open a profile · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Inner as ProfileScreenInner
  participant Did as useResolveDidQuery
  participant Profile as useProfileQuery
  participant Loaded as ProfileScreenLoaded
  participant Section as ProfileFeedSection
  User->>Inner: taps an avatar
  Inner->>Did: resolve the handle
  Inner->>Profile: load the profile
  Profile-->>Inner: profile, after a placeholder
  Inner->>Loaded: renders the header and tabs
  Loaded->>Section: Posts, author feed
  Section-->>User: the account's posts
```

## Key files {#files}

- `src/view/screens/Profile.tsx` · profile screen, tabs that apply
- `src/screens/Profile/Header/` · header, follow and edit
- `src/screens/Profile/Sections/` · feed tab
- `src/view/com/pager/PagerWithHeader.tsx` · pager under a collapsing header
- `src/state/queries/profile.ts` · profile query and mutations
