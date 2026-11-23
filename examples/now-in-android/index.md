---
title: Now in Android App Map
sub: How the app works, one module at a time · **tap a module or a box** to open its map
modules:
- app-shell
- for-you
- bookmarks
- interests
- topic
- search
- settings
links:
  screens:
    ShellN: app-shell
    ForYouN: for-you
    BookmarksN: bookmarks
    InterestsN: interests
    TopicN: topic
    SearchN: search
    SettingsN: settings
  services:
    ForYouS: for-you
    BookmarksS: bookmarks
    InterestsS: interests
    TopicS: topic
    SearchS: search
    SettingsS: settings
    ShellS: app-shell
---

## Screens · how the user moves

Every screen is a `NavKey` on one of three per-tab back stacks (`NavigationState.subStacks`), not
a single shared stack — switching bottom-nav tabs only swaps which sub-stack `NavDisplay` shows,
and each tab remembers where you left it. Settings opens as a dialog over any of them, not a
destination.

```mermaid
flowchart TB
  subgraph shell [App Shell]
    ShellN["MainActivity<br/>NiaApp"]
  end
  subgraph foryou [For You]
    ForYouN["For You<br/>ForYouScreen"]
  end
  subgraph bookmarks [Bookmarks]
    BookmarksN["Saved<br/>BookmarksScreen"]
  end
  subgraph interests [Interests]
    InterestsN["Interests<br/>InterestsScreen"]
  end
  subgraph topic [Topic]
    TopicN["Topic detail<br/>TopicScreen"]
  end
  subgraph search [Search]
    SearchN["Search<br/>SearchScreen"]
  end
  subgraph settings [Settings]
    SettingsN["Settings dialog<br/>SettingsDialog"]
  end
  ShellN -->|bottom nav| ForYouN
  ShellN -->|bottom nav| BookmarksN
  ShellN -->|bottom nav| InterestsN
  ShellN -->|gear icon, any tab| SettingsN
  ShellN -->|top app bar search icon| SearchN
  ForYouN -->|tap a topic chip| TopicN
  InterestsN -->|tap a topic row| TopicN
  SearchN -->|tap a topic result| TopicN
  SearchN -->|tap a news result| TopicN
```

- `───▷` opens
- `▭` tap to open its module

## Services · what the screens call {#services}

Screens never touch the network or the database: they call a repository, or a use case in
`core/domain` that combines repositories.

```mermaid
flowchart LR
  subgraph Screens
    ShellS["App Shell"]
    ForYouS["For You"]
    BookmarksS["Bookmarks"]
    InterestsS["Interests"]
    TopicS["Topic"]
    SearchS["Search"]
    SettingsS["Settings"]
  end
  subgraph UseCases ["core/domain"]
    GetTopicsUse["GetFollowableTopicsUseCase"]
    GetSearchUse["GetSearchContentsUseCase"]
    GetRecentUse["GetRecentSearchQueriesUseCase"]
  end
  subgraph Repos ["core/data repositories"]
    UserNewsRepo["UserNewsResourceRepository"]
    UserDataRepo["UserDataRepository"]
    TopicsRepo["TopicsRepository"]
    SearchContentsRepo["SearchContentsRepository"]
    RecentSearchRepo["RecentSearchRepository"]
    SyncMgr["SyncManager"]
  end
  ShellS -->|userData| UserDataRepo
  ShellS -->|observeAllForFollowedTopics, observeAllBookmarked| UserNewsRepo
  ForYouS -->|observeAllForFollowedTopics| UserNewsRepo
  ForYouS -->|invoke| GetTopicsUse
  ForYouS -->|isSyncing| SyncMgr
  BookmarksS -->|observeAllBookmarked| UserNewsRepo
  BookmarksS -->|setNewsResourceBookmarked| UserDataRepo
  InterestsS -->|invoke, sortBy| GetTopicsUse
  InterestsS -->|setTopicIdFollowed| UserDataRepo
  TopicS -->|getTopic| TopicsRepo
  TopicS -->|observeAll, filterTopicIds| UserNewsRepo
  SearchS -->|invoke, query| GetSearchUse
  SearchS -->|invoke| GetRecentUse
  SearchS -->|getSearchContentsCount| SearchContentsRepo
  SearchS -->|insertOrReplaceRecentSearch| RecentSearchRepo
  SettingsS -->|setThemeBrand, setDarkThemeConfig| UserDataRepo
  GetTopicsUse -->|getTopics, userData| TopicsRepo
  GetTopicsUse -->|followedTopics| UserDataRepo
  GetSearchUse -->|searchContents| SearchContentsRepo
  GetRecentUse -->|getRecentSearchQueries| RecentSearchRepo
```

- `───▷` calls, labelled with the method

## Data · offline first {#data}

Every repository reads `Flow`s backed by the Room database. A separate `SyncManager`/`SyncWorker`
pulls from the network and writes into that same database, so screens update when a sync lands.

```mermaid
flowchart LR
  subgraph Sync ["sync"]
    SyncMgr["SyncManager"]
    SyncWorker["SyncWorker"]
  end
  subgraph Repos ["core/data repositories"]
    UserNewsRepo["UserNewsResourceRepository"]
    NewsRepo["NewsRepository"]
    TopicsRepo["TopicsRepository"]
    RecentSearchRepo["RecentSearchRepository"]
    UserDataRepo["UserDataRepository"]
  end
  subgraph Storage ["database and network"]
    NetworkSrc["NiaNetworkDataSource"]
    Database["NiaDatabase"]
    Prefs["NiaPreferencesDataSource"]
  end
  SyncMgr -->|requestSync| SyncWorker
  SyncWorker -->|syncWith| NewsRepo
  SyncWorker -->|syncWith| TopicsRepo
  UserNewsRepo -->|joins topics + news| NewsRepo
  UserNewsRepo -->|joins topics + news| TopicsRepo
  NewsRepo -->|getNewsResources, getNewsResourceChangeList| NetworkSrc
  TopicsRepo -->|getTopics, getTopicChangeList| NetworkSrc
  NewsRepo -->|Room queries| Database
  TopicsRepo -->|Room queries| Database
  RecentSearchRepo -->|Room queries| Database
  UserDataRepo -->|reads and writes| Prefs
```

- `───▷` calls, labelled with the method
