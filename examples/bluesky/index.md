---
title: Bluesky App Map
sub: How the React Native app works, one module at a time · **tap a module or a box** to open its map
modules:
- launch
- sign-in
- sign-up
- home
- post-thread
- composer
- search
- notifications
- profile
links:
  screens:
    SplashN: launch
    LoggedOutN: launch
    LoginN: sign-in
    SignupN: sign-up
    HomeN: home
    ThreadN: post-thread
    ComposerN: composer
    SearchN: search
    NotifN: notifications
    ProfileN: profile
  services:
    LaunchS: launch
    SignInS: sign-in
    SignUpS: sign-up
    HomeS: home
    ThreadS: post-thread
    ComposerS: composer
    SearchS: search
    NotifS: notifications
    ProfileS: profile
---

## Screens · how the user moves

`App` restores the persisted state and the last session, then renders `Shell`. Signed out, the shell shows `LoggedOut`: a splash with **Create account** and **Sign in**. Signed in, it shows a bottom-tab navigator (Home, Search, Messages, Notifications, Profile) where every tab is its own native stack; post threads, profiles and feeds are pushed onto whichever tab you are in, and the composer opens over everything from the floating button or a reply.

```mermaid
flowchart TB
  subgraph launch [Launch]
    SplashN["Splash and app shell<br/>InnerApp · Shell"]
    LoggedOutN["Signed out<br/>LoggedOut · NativeSplashScreen"]
  end
  subgraph signin [Sign in]
    LoginN["Sign in<br/>Login · LoginForm"]
  end
  subgraph signup [Sign up]
    SignupN["Create account<br/>Signup · StepInfo"]
  end
  subgraph home [Home]
    HomeN["Home feeds<br/>HomeScreen · PostFeed"]
  end
  subgraph thread [Post thread]
    ThreadN["A post and its replies<br/>PostThread"]
  end
  subgraph composer [Composer]
    ComposerN["New post or reply<br/>ComposePost"]
  end
  subgraph search [Search]
    SearchN["Explore and search<br/>SearchScreenShell"]
  end
  subgraph notifications [Notifications]
    NotifN["Notifications<br/>NotificationsScreen"]
  end
  subgraph profile [Profile]
    ProfileN["A profile<br/>ProfileScreenInner"]
  end
  SplashN -->|no session| LoggedOutN
  LoggedOutN -->|Sign in| LoginN
  LoggedOutN -->|Create account| SignupN
  LoginN -->|signed in| HomeN
  SignupN -->|account created| HomeN
  SplashN -->|session resumed| HomeN
  HomeN -->|tap a post| ThreadN
  HomeN -->|tap an avatar| ProfileN
  HomeN -->|new post button| ComposerN
  ThreadN -->|Reply| ComposerN
  ThreadN -->|tap an author| ProfileN
  SearchN -->|tap a result| ThreadN
  SearchN -->|tap a person| ProfileN
  NotifN -->|tap a notification| ThreadN
  ProfileN -->|tap a post| ThreadN
```

- `───▷` opens
- `▭` tap to open its module

## Services · what the screens share

Session state lives in a context (`SessionStateContext`, with its API in `SessionApiContext`); everything the server returns goes through TanStack Query hooks in `state/queries/`, keyed per feed, thread or profile and cached between screens. Feeds are fetched through `FeedAPI` implementations, one per kind of feed. Shell state — the composer, the drawer, the signed-out view — sits in small context stores in `state/shell/`.

```mermaid
flowchart LR
  subgraph Screens
    LaunchS["Launch"]
    SignInS["Sign in"]
    SignUpS["Sign up"]
    HomeS["Home"]
    ThreadS["Post thread"]
    ComposerS["Composer"]
    SearchS["Search"]
    NotifS["Notifications"]
    ProfileS["Profile"]
  end
  subgraph State ["contexts and query hooks"]
    Session["useSession · useSessionApi"]
    LoggedOutCtl["useLoggedOutViewControls"]
    FeedQ["usePostFeedQuery"]
    ThreadQ["usePostThread"]
    ComposerCtl["useComposerControls"]
    Prefs["usePreferencesQuery"]
  end
  subgraph Net ["AT Protocol"]
    FeedApi["FeedAPI"]
    Agent["the session's agent"]
  end
  LaunchS -->|resumeSession| Session
  LaunchS -->|setShowLoggedOut| LoggedOutCtl
  SignInS -->|login| Session
  SignUpS -->|createAccount| Session
  HomeS -->|usePostFeedQuery| FeedQ
  HomeS -->|savedFeeds| Prefs
  FeedQ -->|fetch| FeedApi
  ThreadS -->|usePostThread| ThreadQ
  ThreadS -->|openComposer| ComposerCtl
  ComposerS -->|closeComposer| ComposerCtl
  ProfileS -->|usePostFeedQuery| FeedQ
  SearchS -->|searchPosts, searchActors| Agent
  NotifS -->|getGroupedNotifications| Agent
  FeedApi -->|getTimeline, getFeed| Agent
  ThreadQ -->|getPostThreadV2| Agent
  ComposerS -->|createRecord| Agent
```

- `───▷` calls, labelled with the method or what it reads
- `▭` tap to open its module
