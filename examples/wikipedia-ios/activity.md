---
title: Activity Module
sub: The Activity tab — your reading time, articles read and saved, a timeline of everything you read and edited, and your editing impact when logged in.
card_title: Activity
card: Reading insights, timeline and impact
screenshots:
- file: shots/activity/01_tab.jpg
  caption: 'Activity when logged out: reading insights and a login prompt'
---

## What it does {#what}

`WMFActivityTabViewController` hosts the SwiftUI `WMFActivityTabView`, all of it computed on the device from your reading history except the editing parts. Each time the tab appears, `fetchData()` loads five things in parallel — reading insights (time read in the last 7 days, total articles read, when you last read, weekly reads this month, top categories), saved-article counts, the timeline, and, only when logged in, your global edit count and user impact — and keeps the loading state up for at least 500 ms so it never flickers. The timeline groups every article you read or edited by day; tapping a row opens the article, and swiping deletes it from history. Logged in, the tab adds your contributions, all-time impact, recent edit activity, article views and most-viewed edits; logged out, it offers login. If you have read and saved nothing and the Explore feed is on, it shows a call to action instead. **Customize** turns each section on or off, the menu can clear the whole reading history, and a Year in Review card appears in its season.

## Logic · class diagram {#classes}

One view model fans out to a small view model per section, each with its own fetch.

```mermaid
classDiagram
  direction LR
  class WMFActivityTabViewController {
    <<page>>
    presentFullLoginFlow()
    userDidTapCustomize()
    userDidTapClearReadingHistory()
  }
  class WMFActivityTabViewModel {
    <<view-model>>
    authenticationState · isLoading
    shouldShowExploreCTA · globalEditCount
    fetchData()
    updateAuthenticationState()
  }
  class ArticlesReadViewModel {
    <<view-model>>
    hoursRead · minutesRead
    totalArticlesRead · weeklyReads · topCategories
    fetch()
  }
  class ArticlesSavedViewModel {
    <<view-model>>
    articlesSavedAmount
    fetch()
  }
  class TimelineViewModel {
    <<view-model>>
    onTapArticle
    fetch()
  }
  class ContributionsViewModel { <<view-model>> }
  class AllTimeImpactViewModel { <<view-model>> }
  class WMFActivityTabCustomizeViewModel { <<view-model>> }
  class WMFActivityTabDataController {
    <<data controller>>
    getTimeReadPast7Days()
    getArticlesRead()
    getTopCategories()
    getGlobalEditCount()
    getUserImpactData()
  }
  WMFActivityTabViewController --> WMFActivityTabViewModel : viewModel
  WMFActivityTabViewModel --> ArticlesReadViewModel : articlesReadViewModel
  WMFActivityTabViewModel --> ArticlesSavedViewModel : articlesSavedViewModel
  WMFActivityTabViewModel --> TimelineViewModel : timelineViewModel
  WMFActivityTabViewModel --> ContributionsViewModel : logged in
  WMFActivityTabViewModel --> AllTimeImpactViewModel : logged in
  WMFActivityTabViewModel --> WMFActivityTabCustomizeViewModel : customizeViewModel
  ArticlesReadViewModel ..> WMFActivityTabDataController : getTimeReadPast7Days()
  WMFActivityTabViewModel ..> WMFActivityTabDataController : getUserImpactData()
```

- `──▷` holds
- `┄┄▷` uses

## Screen · view composition {#widgets}

```mermaid
classDiagram
  direction TB
  class WMFActivityTabHostingController { <<hosting>> }
  class WMFActivityTabView { <<SwiftUI>> }
  class WMFActivityTabInfoCardView { <<card>> }
  class ContributionsView { <<section>> }
  class CombinedImpactView { <<section>> }
  class TopViewedEditsView { <<section>> }
  class TimelineSectionView { <<one day>> }
  class TimelineRowView { <<row>> }
  class WMFActivityTabYearInReviewCardView { <<card>> }
  WMFActivityTabHostingController *-- WMFActivityTabView
  WMFActivityTabView *-- WMFActivityTabInfoCardView : reading insights
  WMFActivityTabView *-- WMFActivityTabYearInReviewCardView
  WMFActivityTabView *-- ContributionsView : logged in
  WMFActivityTabView *-- CombinedImpactView : logged in
  WMFActivityTabView *-- TopViewedEditsView : logged in
  WMFActivityTabView *-- TimelineSectionView
  TimelineSectionView *-- TimelineRowView
```

- `◆──` contains

## Open the Activity tab · sequence {#sequence}

Five fetches run at once; the editing ones return early when you are logged out.

```mermaid
sequenceDiagram
  actor User
  participant Tab as WMFActivityTabViewController
  participant Model as WMFActivityTabViewModel
  participant Read as ArticlesReadViewModel
  participant Timeline as TimelineViewModel
  participant Data as WMFActivityTabDataController
  User->>Tab: open Activity
  Tab->>Model: fetchData()
  Model->>Read: fetch()
  Read->>Data: getTimeReadPast7Days() and four more
  Model->>Timeline: fetch()
  Model->>Data: getGlobalEditCount(), logged in only
  Model->>Data: getUserImpactData(), logged in only
  Note over Model: loading stays at least 500 ms
  Model-->>User: insights, impact and the timeline
  User->>Timeline: tap a row
  Timeline-->>Tab: onTapArticle, pushes the article
```

## Key files {#files}

- `Wikipedia/Code/ActivityTabViewController.swift` · Activity tab, login, customize, clear history
- `WMFComponents/Sources/WMFComponents/Components/Activity Tab/` · views and the tab view model
- `WMFComponents/Sources/WMFComponents/Components/Activity Tab/View Models/` · per-section view models
- `WMFData/Sources/WMFData/Data Controllers/Activity Tab/` · reading and impact data
