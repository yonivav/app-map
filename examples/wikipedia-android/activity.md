---
title: Activity Module
sub: The Activity tab — reading insights from the device's history, and for logged-in readers their editing impact, donations, games and a timeline.
card_title: Activity
card: Reading insights, impact and timeline
screenshots:
- file: shots/activity/01_intro.jpg
  caption: The Activity onboarding
- file: shots/activity/02_tab.jpg
  caption: 'Logged out: login prompt and Year in Review card'
---

## What it does {#what}

`ActivityTabFragment` shows a Compose screen built from modules, each with its own `UiState` (loading, success, error). `loadAll()` always loads the reading history and the Year in Review entry; everything else needs an account, so logged out the tab stops there and shows a login prompt. Reading history is read straight from Room, after a 500 ms pause for the loading state: time spent reading in the last 7 days, distinct articles read in the last 30 days and in each of the last 4 weeks, when you last read, articles saved in the last 30 days (with the 4 newest), and this month's top categories. Logged in, it also loads donation results, Wikipedia games stats, your impact — fetched from the Growth user-impact API at most once every 12 hours per wiki and cached in `Prefs`, because that API is rate limited — and a paged timeline of reads and edits. Each module can be hidden from **Customize**, and the first visit shows an onboarding screen.

## Logic · class diagram {#classes}

One view model with a state flow per module; the fragment just collects them into the Compose screen.

```mermaid
classDiagram
  direction LR
  class ActivityTabFragment { <<page>> }
  class ActivityTabViewModel {
    <<view-model>>
    loadAll()
    loadReadingHistory()
    loadImpact()
    loadDonationResults()
    loadWikiGamesStats()
    refreshTimeline()
  }
  class ReadingHistory {
    <<data>>
    timeSpentThisWeek · articlesReadThisMonth
    articlesReadByWeek · topCategories
  }
  class ActivityTabModules {
    <<data>>
    isModuleEnabled()
  }
  class AppDatabase {
    <<Room>>
    historyEntryDao()
    readingListPageDao()
    categoryDao()
  }
  class ServiceFactory {
    <<network>>
    getCoreRest()
  }
  class ActivityTabOnboardingActivity { <<activity>> }
  class ActivityTabCustomizationActivity { <<activity>> }
  ActivityTabFragment --> ActivityTabViewModel
  ActivityTabViewModel ..> ReadingHistory : builds
  ActivityTabViewModel ..> AppDatabase : historyEntryDao()
  ActivityTabViewModel ..> ServiceFactory : getCoreRest() user impact
  ActivityTabFragment ..> ActivityTabModules : which modules show
  ActivityTabFragment ..> ActivityTabOnboardingActivity : first visit
  ActivityTabFragment ..> ActivityTabCustomizationActivity : Customize
```

- `──▷` holds
- `┄┄▷` uses · opens

## Screen · composition {#widgets}

```mermaid
classDiagram
  direction TB
  class ActivityTabLoggedInScreen { <<composable>> }
  class ActivityTabLoggedOutScreen { <<composable>> }
  class ReadingHistoryModule { <<composable>> }
  class TopCategoriesCard { <<composable>> }
  class ImpactModule { <<composable>> }
  class AllTimeImpactCard { <<composable>> }
  class EditingInsightsModule { <<composable>> }
  class DonationModule { <<composable>> }
  class TimelineModule { <<composable>> }
  ActivityTabLoggedInScreen *-- ReadingHistoryModule
  ReadingHistoryModule *-- TopCategoriesCard
  ActivityTabLoggedInScreen *-- ImpactModule
  ImpactModule *-- AllTimeImpactCard
  ActivityTabLoggedInScreen *-- EditingInsightsModule
  ActivityTabLoggedInScreen *-- DonationModule
  ActivityTabLoggedInScreen *-- TimelineModule
  ActivityTabLoggedOutScreen *-- ReadingHistoryModule
```

- `◆──` contains

## Open the Activity tab, logged in · sequence {#sequence}

Reading insights never leave the device; impact is cached for 12 hours.

```mermaid
sequenceDiagram
  actor User
  participant Fragment as ActivityTabFragment
  participant Model as ActivityTabViewModel
  participant DB as AppDatabase
  participant Api as ServiceFactory
  User->>Fragment: open Activity
  Fragment->>Model: loadAll()
  Model->>Model: loadReadingHistory(), waits 500 ms
  Model->>DB: historyEntryDao() time and counts
  Model->>DB: readingListPageDao(), categoryDao()
  Model->>Model: loadImpact()
  Note over Model: cached response used if younger than 12 h
  Model->>Api: getCoreRest() user impact
  Model->>Model: refreshTimeline()
  Model-->>Fragment: UiState success per module
  Fragment-->>User: insights, impact, timeline
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/activitytab/ActivityTabFragment.kt` · Activity tab
- `app/src/main/java/org/wikipedia/activitytab/ActivityTabViewModel.kt` · module states and loading
- `app/src/main/java/org/wikipedia/activitytab/ActivityTabLoggedInScreen.kt` · logged-in screen
- `app/src/main/java/org/wikipedia/activitytab/ReadingHistoryModule.kt` · reading insights
- `app/src/main/java/org/wikipedia/activitytab/ImpactModule.kt` · editing impact
- `app/src/main/java/org/wikipedia/activitytab/timeline/` · paged timeline
