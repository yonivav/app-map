---
title: Wikipedia Android App Map
sub: How the Android app works, one module at a time · **tap a module or a box** to open its map
modules:
- launch
- home
- article
- search
- saved
- activity
- places
- settings
links:
  screens:
    MainN: launch
    OnboardN: launch
    PersonalN: launch
    HomeN: home
    PageN: article
    SearchN: search
    HistoryN: search
    SavedN: saved
    ListN: saved
    ActivityN: activity
    MoreN: settings
    PlacesN: places
    SettingsN: settings
  services:
    LaunchS: launch
    HomeS: home
    ArticleS: article
    SearchS: search
    SavedS: saved
    ActivityS: activity
    PlacesS: places
    SettingsS: settings
---

## Screens · how the user moves

`MainActivity` holds `MainFragment`, a bottom navigation over a pager of five tabs — Home, Saved, Search (your history, with a search bar that opens the search screen), Activity and **More**, which is not a page but a bottom sheet with the account, watchlist, games, Places and Settings. On a first launch the onboarding activity runs on top, followed by the personalization screens. Every article opens in `PageActivity`, which keeps its own back stack of pages and browser-like tabs.

```mermaid
flowchart TB
  subgraph launch [Launch]
    MainN["Tabs<br/>MainFragment"]
    OnboardN["Onboarding<br/>InitialOnboardingActivity"]
    PersonalN["Interests and feed<br/>PersonalizationActivity"]
  end
  subgraph home [Home]
    HomeN["Home · Community and For You<br/>HomeFragment"]
  end
  subgraph article [Article]
    PageN["Article<br/>PageActivity"]
  end
  subgraph search [Search]
    HistoryN["Search tab · history<br/>HistoryFragment"]
    SearchN["Search<br/>SearchActivity"]
  end
  subgraph saved [Saved]
    SavedN["Saved<br/>ReadingListsFragment"]
    ListN["One list<br/>ReadingListActivity"]
  end
  subgraph activity [Activity]
    ActivityN["Activity<br/>ActivityTabFragment"]
  end
  subgraph places [Places]
    PlacesN["Map<br/>PlacesActivity"]
  end
  subgraph settings [Settings]
    MoreN["More menu<br/>MenuNavTabDialog"]
    SettingsN["Settings<br/>SettingsActivity"]
  end
  MainN -->|first launch| OnboardN
  OnboardN -->|done| PersonalN
  PersonalN --> HomeN
  MainN -->|tab 0| HomeN
  HomeN -->|tap a card| PageN
  PageN -->|tap a link| PageN
  MainN -->|tab 2| HistoryN
  HistoryN -->|search bar| SearchN
  HistoryN -->|tap an entry| PageN
  SearchN -->|tap a result| PageN
  MainN -->|tab 1| SavedN
  SavedN -->|tap a list| ListN
  SavedN -->|tap an article| PageN
  MainN -->|tab 3| ActivityN
  ActivityN -->|tap a read article| PageN
  MainN -->|tab 4| MoreN
  MoreN --> PlacesN
  MoreN --> SettingsN
  PlacesN -->|tap a place, then read| PageN
```

- `───▷` opens
- `▭` tap to open its module

## Services · what the screens share

The app's state lives in a Room database (`AppDatabase`: history, reading lists, saved pages, categories) and `Prefs`; network calls go through Retrofit services from `ServiceFactory` (the Action API and the REST API of each wiki). Two WorkManager workers do the background work: one downloads saved pages for offline reading, the other syncs reading lists with the account.

```mermaid
flowchart LR
  subgraph Screens
    LaunchS["Launch"]
    HomeS["Home"]
    ArticleS["Article"]
    SearchS["Search"]
    SavedS["Saved"]
    ActivityS["Activity"]
    PlacesS["Places"]
    SettingsS["Settings"]
  end
  subgraph App ["app state"]
    App1["WikipediaApp"]
    PrefsN["Prefs"]
    DB["AppDatabase"]
  end
  subgraph Net ["network"]
    Service["ServiceFactory"]
    Bridge["CommunicationBridge"]
  end
  subgraph Work ["background workers"]
    SavedSync["SavedPageSyncService"]
    ListSync["ReadingListSyncAdapter"]
  end
  LaunchS -->|isInitialOnboardingEnabled| PrefsN
  HomeS -->|getFeedFeatured| Service
  HomeS -->|homePreferenceSelection| PrefsN
  ArticleS -->|getSummaryResponse| Service
  ArticleS -->|execute| Bridge
  ArticleS -->|historyEntryDao| DB
  SearchS -->|prefixSearchResponse| Service
  SearchS -->|recentSearchDao| DB
  SavedS -->|readingListPageDao| DB
  DB -->|enqueue| SavedSync
  SavedS -->|manualSync| ListSync
  SavedSync -->|reqMobileHTML| Service
  ListSync -->|getChangesSince| Service
  ActivityS -->|historyEntryDao| DB
  PlacesS -->|getGeoSearch| Service
  SettingsS -->|colors, languages, sync| PrefsN
  App1 -->|languageState| PrefsN
```

- `───▷` calls, labelled with the method or what it reads
- `▭` tap to open its module
