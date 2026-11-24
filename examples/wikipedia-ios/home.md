---
title: Home Module
sub: The Home tab's two feeds — a personal For You feed and the Community feed of featured, top read, news and on-this-day cards — in one SwiftUI screen.
card_title: Home
card: For You and Community feeds
screenshots:
- file: shots/home/01_community.jpg
  caption: 'Community: today''s featured article, in the classic Explore feed'
- file: shots/home/02_community_scrolled.jpg
  caption: Top read, with today's game above
- file: shots/home/03_for_you.jpg
  caption: 'For You: a card based on your interests'
---

## What it does {#what}

`HomeCoordinator` builds the Home tab: a UIKit `HomeViewController` hosting the SwiftUI `WMFHomeView`, with a **For You / Community** segmented control and a language menu in the navigation bar. **For You** is fetched from `WMFHomeDataController` for the selected wiki and has three modules — based on your interests, because you read, and continue reading — each of which can be hidden, as can single cards. **Community** is, unless the phase-2 developer flag is on, the classic Explore feed embedded as a child view controller: `ExploreViewController` shows a Core Data–backed list of `WMFContentGroup` cards produced by `WMFExploreFeedContentController` from content sources — related pages, continue reading and suggested edits once, plus per preferred language a daily game, nearby places, the featured article / top read / in the news / picture of the day feed, a random article, announcements and on this day. Pull to refresh asks every source to update for today; scrolling to the end loads the previous day. The feeds reload when the day changes, and tapping a card pushes the article on the Home tab's navigation stack. Card actions (save, share, hide) are logged through the coordinator's closures.

## Logic · class diagram {#classes}

A UIKit shell around a SwiftUI view model, with the legacy Core Data feed plugged in as the Community segment.

```mermaid
classDiagram
  direction LR
  class HomeCoordinator {
    <<coordinator>>
    homeViewController
    start()
    makeHomeViewController()
  }
  class HomeViewController {
    <<page>>
    viewModel
    embeddedExploreViewController()
    embedHostingController()
  }
  class WMFHomeViewModel {
    <<view-model>>
    selectedTab · selectedLanguage
    forYouViewModel · communityPages
    loadCurrentTabFeedIfNeeded()
    loadForYouFeedIfNeeded()
    loadCommunityFeedIfNeeded()
    refreshFeedsIfDayChanged()
    hideForYouModule() · hideCard()
  }
  class WMFHomeDataController {
    <<data controller>>
    fetchForYou()
    fetchCommunity()
    hiddenCardKeys()
  }
  class ExploreViewController {
    <<page>>
    fetchedResultsController
    refresh()
  }
  class WMFExploreFeedContentController {
    <<service>>
    contentSources
  }
  class WMFContentGroup { <<Core Data entity>> }
  class WMFFeedContentSource { <<content source>> }
  class WMFOnThisDayContentSource { <<content source>> }
  class WMFContinueReadingContentSource { <<content source>> }
  class WMFRelatedPagesContentSource { <<content source>> }
  class WMFNearbyContentSource { <<content source>> }
  HomeCoordinator ..> HomeViewController : makeHomeViewController()
  HomeViewController --> WMFHomeViewModel : viewModel
  WMFHomeViewModel --> WMFHomeDataController : dataController
  HomeViewController --> ExploreViewController : Community segment
  ExploreViewController ..> WMFExploreFeedContentController : update the feed sources
  WMFExploreFeedContentController o-- WMFFeedContentSource
  WMFExploreFeedContentController o-- WMFOnThisDayContentSource
  WMFExploreFeedContentController o-- WMFContinueReadingContentSource
  WMFExploreFeedContentController o-- WMFRelatedPagesContentSource
  WMFExploreFeedContentController o-- WMFNearbyContentSource
  WMFFeedContentSource ..> WMFContentGroup : creates
  ExploreViewController ..> WMFContentGroup : fetched results
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · view composition {#widgets}

SwiftUI on top, UIKit cards underneath when Community shows the classic feed.

```mermaid
classDiagram
  direction TB
  class HomeViewController { <<page>> }
  class WMFHomeHostingController { <<hosting>> }
  class WMFHomeView { <<SwiftUI>> }
  class WMFForYouView { <<SwiftUI>> }
  class WMFForYouViewModel {
    <<view-model>>
    pages · moduleVisibility
  }
  class WMFHomeEmbeddedCommunityView { <<SwiftUI>> }
  class WMFCommunityFeedView { <<phase 2>> }
  class ExploreViewController { <<page>> }
  class ExploreCardViewController {
    <<card>>
    contentGroup
  }
  HomeViewController *-- WMFHomeHostingController
  WMFHomeHostingController *-- WMFHomeView
  WMFHomeView *-- WMFForYouView : For You
  WMFForYouView --> WMFForYouViewModel
  WMFHomeView *-- WMFHomeEmbeddedCommunityView : Community
  WMFHomeView *-- WMFCommunityFeedView : Community, phase 2
  WMFHomeEmbeddedCommunityView *-- ExploreViewController
  ExploreViewController *-- ExploreCardViewController : one per content group
```

- `◆──` contains
- `──▷` reads model

## Pull to refresh the Community feed · sequence {#sequence}

Every source writes content groups into Core Data; the fetched-results controller animates the new cards in.

```mermaid
sequenceDiagram
  actor User
  participant Explore as ExploreViewController
  participant Feed as WMFExploreFeedContentController
  participant Source as WMFFeedContentSource
  participant Store as MWKDataStore
  participant Card as ExploreCardViewController
  User->>Explore: pull down
  Explore->>Explore: refresh()
  Explore->>Feed: update every source for today
  Feed->>Source: load content for the date
  Source->>Store: creates or updates WMFContentGroup rows
  Store-->>Explore: fetched results change
  Explore->>Card: contentGroup
  Card-->>User: featured article, top read, news and more
  User->>Card: tap an article
  Card->>Explore: pushes the article
```

## Key files {#files}

- `Wikipedia/Code/HomeCoordinator.swift` · builds the Home tab and logs card actions
- `Wikipedia/Code/HomeViewController.swift` · hosts the SwiftUI home, embeds Explore
- `WMFComponents/Sources/WMFComponents/Components/Home/` · home, For You and Community views
- `Wikipedia/Code/ExploreViewController.swift` · classic Explore feed
- `Wikipedia/Code/ExploreCardViewController.swift` · one feed card
- `WMF Framework/WMFExploreFeedContentController.m` · content sources and updates
- `WMFData/Sources/WMFData/Data Controllers/Home/` · For You and Community data
