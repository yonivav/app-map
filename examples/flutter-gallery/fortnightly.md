---
title: Fortnightly Study
sub: A news-app study with a trending hashtag bar and a feed of article previews, with a section menu in a drawer.
card_title: Fortnightly
card: News feed layout study
screenshots:
- file: shots/fortnightly/01_feed.jpg
  caption: Hashtags and the lead story
- file: shots/fortnightly/02_feed.jpg
  caption: Horizontal previews
- file: shots/fortnightly/03_menu.jpg
  caption: The section menu drawer
---

## What it does {#what}

Fortnightly is a single-route `MaterialApp` at `/fortnightly` that shows how one set of content adapts from a phone to a wide screen. On a phone it is a `Scaffold` with the Fortnightly wordmark in the app bar, a search button that does nothing, and a drawer with the section menu — Front Page, World, US, Politics, Business, Tech, Science, Sports, Travel, Culture. The body is a horizontal bar of five trending hashtags followed by the article feed: one large vertical preview, then horizontal previews separated by thin dividers and a thicker section divider. On desktop the same pieces become three columns — the menu, the article feed and a column of stock tickers and video previews — under the hashtag bar. All content is static: `ArticleData` objects with an image, a category, a title and an optional snippet, built in code each time the feed is built.

## Logic · class diagram {#classes}

No state at all: top-level builder functions return the lists of widgets, and the app picks a layout by screen width.

```mermaid
classDiagram
  direction LR
  class FortnightlyApp {
    <<app>>
    defaultRoute
  }
  class _FortnightlyHomeMobile { <<layout>> }
  class _FortnightlyHomeDesktop { <<layout>> }
  class ArticleData {
    <<data>>
    imageUrl · imageAspectRatio
    category · title · snippet
  }
  class HorizontalArticlePreview {
    <<widget>>
    data · minutes
  }
  class VerticalArticlePreview {
    <<widget>>
    data · width
  }
  class VideoPreview {
    <<widget>>
    data · time
  }
  class StockItem {
    <<widget>>
    ticker · price · percent
  }
  FortnightlyApp *-- _FortnightlyHomeMobile : phone
  FortnightlyApp *-- _FortnightlyHomeDesktop : desktop
  HorizontalArticlePreview --> ArticleData : data
  VerticalArticlePreview --> ArticleData : data
  VideoPreview --> ArticleData : data
  _FortnightlyHomeDesktop *-- StockItem
  _FortnightlyHomeDesktop *-- VideoPreview
```

- `◆──` contains
- `──▷` reads model

## Screen · widget composition {#widgets}

The phone feed is one `ListView`: hashtags first, then the previews in order.

```mermaid
classDiagram
  direction TB
  class _FortnightlyHomeMobile { <<layout>> }
  class NavigationMenu {
    <<drawer>>
    isCloseable
  }
  class MenuItem {
    <<widget>>
    title · header
  }
  class HashtagBar { <<widget>> }
  class VerticalArticlePreview { <<widget>> }
  class HorizontalArticlePreview { <<widget>> }
  class FadeInImagePlaceholder { <<image>> }
  _FortnightlyHomeMobile *-- NavigationMenu : drawer
  NavigationMenu *-- MenuItem : 10 sections
  _FortnightlyHomeMobile *-- HashtagBar
  _FortnightlyHomeMobile *-- VerticalArticlePreview : lead story
  _FortnightlyHomeMobile *-- HorizontalArticlePreview : the rest
  HorizontalArticlePreview *-- FadeInImagePlaceholder
  VerticalArticlePreview *-- FadeInImagePlaceholder
```

- `◆──` contains

## Open the section menu · sequence {#sequence}

The only interaction is the drawer; everything else is layout.

```mermaid
sequenceDiagram
  actor User
  participant App as FortnightlyApp
  participant Mobile as _FortnightlyHomeMobile
  participant Bar as HashtagBar
  participant Menu as NavigationMenu
  App->>App: narrow screen, not desktop
  App->>Mobile: phone layout
  Mobile->>Bar: five trending hashtags
  Mobile->>Mobile: builds the article previews
  Mobile-->>User: wordmark, hashtags and the feed
  User->>Mobile: swipe in from the edge
  Mobile->>Menu: drawer opens, isCloseable
  Menu-->>User: Front Page to Culture, with a close button
```

## Key files {#files}

- `lib/studies/fortnightly/app.dart` · app and its phone and desktop layouts
- `lib/studies/fortnightly/shared.dart` · articles, previews, menu, stocks, theme
