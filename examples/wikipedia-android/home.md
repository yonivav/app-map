---
title: Home Module
sub: The Home tab in Compose — a Community feed of each day's featured content and a personalized For You feed of modules, with a language menu.
card_title: Home
card: Community and For You feeds in Compose
screenshots:
- file: shots/home/01_feed.jpg
  caption: 'Community: today''s featured article under a day header'
- file: shots/home/02_scrolled.jpg
  caption: Top read further down the same day
- file: shots/home/03_for_you.jpg
  caption: 'For You: modules of cards, here places you love'
---

## What it does {#what}

`HomeFragment` sets a Compose `HomeScreen` with a toolbar (language menu, tabs counter, notifications) and two tabs. The tab it opens on comes from the onboarding choice: For You for a personalized preference, otherwise Community. **Community** fetches one day at a time from the REST `feed/featured` endpoint of the selected wiki and turns it into cards under a day header — featured article, top read, did you know, in the news, on this day (the first 2 events) and picture of the day; **Load more** fetches the day before, and a failed day is retried rather than skipped. **For You** loads batches of modules — based on your interests, continue reading, because you read, places near you, discover, random, games and read-aloud — each a horizontal pager of cards; places and discover are added on their own as they become available. Cards and whole modules can be hidden from their overflow menu (with **Undo**), and the hidden ones are remembered. Every interaction is a `HomeAction` sent up to the fragment, which calls the view model or navigates: a card opens the article in `PageActivity`, a news story opens its list, the picture opens the gallery. Pull to refresh reloads the current tab.

## Logic · class diagram {#classes}

Unidirectional flow: state flows down from the view model, actions flow up to the fragment.

```mermaid
classDiagram
  direction LR
  class HomeFragment {
    <<page>>
    viewModel
    handleHomeAction()
    selectTab()
    updateLanguage()
  }
  class HomeViewModel {
    <<view-model>>
    wikiSite · selectedTab · tabsState
    loadCommunityContent()
    loadForYouContent()
    refreshCommunityContent()
    refreshForYouContent()
    selectTab()
    hideCommunityCard()
    hideModule()
  }
  class HomeTab {
    <<enum>>
    COMMUNITY · FOR_YOU
  }
  class CommunityContentState {
    <<state>>
    cards · isLoadingMore · canLoadMore
  }
  class ForYouContentState {
    <<state>>
    modules
  }
  class ForYouModule {
    <<sealed>>
    cards
    moduleKey()
  }
  class HomeAction { <<sealed>> }
  class ServiceFactory {
    <<network>>
    getRest()
  }
  class FeaturedArticleCard { <<card>> }
  class TopReadCard { <<card>> }
  class NewsCard { <<card>> }
  class OnThisDayCard { <<card>> }
  class FeaturedImageCard { <<card>> }
  HomeFragment --> HomeViewModel : viewModel
  HomeViewModel --> HomeTab : selectedTab
  HomeViewModel --> CommunityContentState : communityState
  HomeViewModel --> ForYouContentState : forYouState
  ForYouContentState o-- ForYouModule : modules
  HomeViewModel ..> ServiceFactory : getRest() feed/featured
  CommunityContentState o-- FeaturedArticleCard
  CommunityContentState o-- TopReadCard
  CommunityContentState o-- NewsCard
  CommunityContentState o-- OnThisDayCard
  CommunityContentState o-- FeaturedImageCard
  HomeAction ..> HomeFragment : sent up from the UI
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · composition {#widgets}

```mermaid
classDiagram
  direction TB
  class HomeScreen { <<composable>> }
  class HomeToolbar { <<composable>> }
  class LanguageDropDownMenu { <<composable>> }
  class HomeTabBar { <<composable>> }
  class CommunityContentTab { <<composable>> }
  class DayHeader { <<composable>> }
  class LoadMoreButton { <<composable>> }
  class ForYouContentTab { <<composable>> }
  class ForYouCardContent { <<composable>> }
  class ErrorState { <<composable>> }
  HomeScreen *-- HomeToolbar
  HomeToolbar *-- LanguageDropDownMenu
  HomeScreen *-- HomeTabBar
  HomeScreen *-- CommunityContentTab : Community
  CommunityContentTab *-- DayHeader
  CommunityContentTab *-- LoadMoreButton
  CommunityContentTab *-- ErrorState
  HomeScreen *-- ForYouContentTab : For You
  ForYouContentTab *-- ForYouCardContent
```

- `◆──` contains

## Load more of the Community feed · sequence {#sequence}

Each page is one earlier day; the age only advances after a successful fetch.

```mermaid
sequenceDiagram
  actor User
  participant Tab as CommunityContentTab
  participant Fragment as HomeFragment
  participant Model as HomeViewModel
  participant Api as ServiceFactory
  User->>Tab: tap Load more
  Tab->>Fragment: LoadMoreCommunityContent
  Fragment->>Fragment: handleHomeAction()
  Fragment->>Model: loadCommunityContent()
  Model->>Api: getRest() feed/featured for the day before
  Api-->>Model: featured, top read, news, on this day, picture
  Model->>Model: builds the cards under a day header
  Model-->>Tab: communityState with the new cards
  User->>Tab: tap the featured article
  Tab->>Fragment: PageClick
  Fragment-->>User: opens the article
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/feed/HomeFragment.kt` · Home tab, actions, navigation
- `app/src/main/java/org/wikipedia/feed/HomeViewModel.kt` · both feeds, hiding, languages
- `app/src/main/java/org/wikipedia/feed/HomeScreen.kt` · toolbar, tabs, language menu
- `app/src/main/java/org/wikipedia/feed/CommunityContentTab.kt` · Community feed
- `app/src/main/java/org/wikipedia/feed/ForYouContentTab.kt` · For You modules
- `app/src/main/java/org/wikipedia/feed/HomeAction.kt` · every UI action
- `app/src/main/java/org/wikipedia/feed/` · card types per feed module
