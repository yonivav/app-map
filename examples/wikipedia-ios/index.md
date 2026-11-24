---
title: Wikipedia iOS App Map
sub: How the iOS app works, one module at a time · **tap a module or a box** to open its map
modules:
- launch
- home
- article
- search
- places
- saved
- activity
- settings
links:
  screens:
    SplashN: launch
    OnboardN: launch
    HomeN: home
    ExploreN: home
    ArticleN: article
    TocN: article
    SearchN: search
    PlacesN: places
    SavedN: saved
    ListsN: saved
    ActivityN: activity
    SettingsN: settings
  services:
    LaunchS: launch
    HomeS: home
    ArticleS: article
    SearchS: search
    PlacesS: places
    SavedS: saved
    ActivityS: activity
    SettingsS: settings
---

## Screens · how the user moves

`SceneDelegate` hands the window to `WMFAppViewController`, a `UITabBarController` that shows a splash while the Core Data store migrates, presents the first-run onboarding once, and then builds five tabs — Home, Places, Saved, Activity, Search — each in its own navigation controller. Articles push onto whichever tab you are in; Settings opens from the profile menu behind the account button in every tab's navigation bar. After 24 hours in the background the app reopens on Home.

```mermaid
flowchart TB
  subgraph launch [Launch]
    SplashN["Splash and migration<br/>SplashScreenViewController"]
    OnboardN["First-run onboarding<br/>AppOnboardingCoordinator"]
  end
  subgraph home [Home]
    HomeN["Home · For You and Community<br/>HomeViewController"]
    ExploreN["Community feed<br/>ExploreViewController"]
  end
  subgraph article [Article]
    ArticleN["Article<br/>ArticleViewController"]
    TocN["Contents<br/>TableOfContentsViewController"]
  end
  subgraph search [Search]
    SearchN["Search<br/>SearchViewController"]
  end
  subgraph places [Places]
    PlacesN["Map of nearby articles<br/>PlacesViewController"]
  end
  subgraph saved [Saved]
    SavedN["Saved<br/>WMFSavedHostingController"]
    ListsN["Reading lists<br/>ReadingListsCoordinator"]
  end
  subgraph activity [Activity]
    ActivityN["Activity<br/>WMFActivityTabViewController"]
  end
  subgraph settings [Settings]
    SettingsN["Settings<br/>SettingsTabViewController"]
  end
  SplashN -->|first launch| OnboardN
  SplashN -->|tab 0| HomeN
  OnboardN -->|done or skip| HomeN
  HomeN -->|Community segment| ExploreN
  HomeN -->|tap a card| ArticleN
  ExploreN -->|tap a card| ArticleN
  ArticleN -->|contents button| TocN
  ArticleN -->|tap a link| ArticleN
  SplashN -->|tab 4| SearchN
  SearchN -->|tap a result| ArticleN
  SplashN -->|tab 1| PlacesN
  PlacesN -->|tap a place| ArticleN
  SplashN -->|tab 2| SavedN
  SavedN -->|Reading lists segment| ListsN
  SavedN -->|tap an article| ArticleN
  SplashN -->|tab 3| ActivityN
  ActivityN -->|tap a read article| ArticleN
  HomeN -->|profile menu, Settings| SettingsN
```

- `───▷` opens
- `▭` tap to open its module

## Services · what the screens share

One `MWKDataStore` (Core Data, owned by the app controller) holds articles, history, saved pages, feed groups and reading lists; the older screens read it directly, while the newer SwiftUI screens go through data controllers in the `WMFData` package. Article pages are rendered HTML from the Page Content Service, cached for offline reading.

```mermaid
flowchart LR
  subgraph Screens
    LaunchS["Launch"]
    HomeS["Home"]
    ArticleS["Article"]
    SearchS["Search"]
    PlacesS["Places"]
    SavedS["Saved"]
    ActivityS["Activity"]
    SettingsS["Settings"]
  end
  subgraph App ["WMF framework"]
    Store["MWKDataStore"]
    Feed["WMFExploreFeedContentController"]
    Summary["ArticleSummaryController"]
    Lists["WMFReadingListsController"]
    Cache["ArticleCacheController"]
    Auth["WMFAuthenticationManager"]
    Location["LocationManager"]
  end
  subgraph Data ["WMFData package"]
    HomeData["WMFHomeDataController"]
    LegacyLists["WMFLegacyReadingListsDataController"]
    ActivityData["WMFActivityTabDataController"]
    SettingsData["WMFSettingsDataController"]
  end
  subgraph Net ["network"]
    SearchF["WMFSearchFetcher"]
    PlaceS["PlaceSearchService"]
    ArticleF["ArticleFetcher"]
  end
  LaunchS -->|performLibraryUpdates| Store
  HomeS -->|updateFeedSources| Feed
  HomeS -->|feed preferences| HomeData
  Feed -->|content groups| Store
  ArticleS -->|mobileHTMLRequest| ArticleF
  ArticleS -->|updateOrCreateArticleSummaryForArticle| Summary
  ArticleS -->|addToReadHistory| Store
  ArticleS -->|save| Lists
  Lists -->|offline copy| Cache
  SearchS -->|fetchArticlesForSearchTerm| SearchF
  PlacesS -->|performSearch| PlaceS
  PlacesS -->|startMonitoringLocation| Location
  SavedS -->|saved articles| LegacyLists
  LegacyLists -->|reads| Store
  SavedS -->|fullSync| Lists
  ActivityS -->|reading history| ActivityData
  ActivityS -->|isLoggedIn| Auth
  SettingsS -->|preferences| SettingsData
  SettingsS -->|logout| Auth
  Summary -->|writes| Store
```

- `───▷` calls, labelled with the method or what it reads
- `▭` tap to open its module
