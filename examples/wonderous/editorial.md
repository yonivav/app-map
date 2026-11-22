---
title: Editorial Module
sub: 'The “information and history” tab: one long, scroll-choreographed article about the wonder.'
card_title: Editorial
card: Scroll-choreographed story of one wonder
screenshots:
- file: shots/editorial/01_story.jpg
  caption: The scroll-driven story begins
- file: shots/editorial/02_pull_quote.jpg
  caption: Arched header, pull quote
- file: shots/editorial/03_history.jpg
  caption: Circular section title over the text
---

## What it does {#what}

A `CustomScrollView` slides over a fixed illustration of the wonder (150, 250 or 280 px tall for screens under 525, under 700 or taller) that shows through a transparent first sliver and fades out over the first 700 px of scroll. The title block — subtitle, hero title, region, a compass divider that folds away once you scroll, and the date range — drifts down at 30 % of the scroll speed and is gone after 500 px. A pinned app bar collapses from 1.2 × the screen width (width capped at 800 px) to 150 px (80 px on screens under 700 px tall); it shows photo 1 clipped to the wonder’s arch (pyramid, flat pyramid, arch, wide arch or spade), turning into a coloured band below 300 px, with a circular title that rolls 180° to “Facts and History”, “Construction” or “Location Info” as each section divider passes the middle of the screen. The article runs history → pull quote over photo 2 that collapses as it scrolls up → callout → construction → YouTube thumbnail (`…/video/`, full-screen player that unlocks landscape) → photos 3 and 4 sliding past each other → location → large quote → a Google map (zoom 3) that opens `…/maps/` as a full-screen hybrid map at zoom 17 (hidden on desktop). Paragraphs open with a drop cap in English only. Four slots can hold this wonder’s first hidden collectible; each wonder uses exactly one of them. Pulling 70 px past the top while dragging pops back to Home, and so does the north-arrow button, which hides once you scroll.

## Logic · class diagram {#classes}

One ScrollController feeds a ValueNotifier of the scroll position; every animated piece listens to it and measures its own place on screen, and the section dividers write the section index back.

```mermaid
classDiagram
  direction LR
  class WonderEditorialScreen {
    <<page>>
    data · contentPadding
  }
  class _WonderEditorialScreenState {
    <<page state>>
    _scroller · _scrollPos · _sectionIndex
    _handleScrollChanged()
    _handleTrackpadScroll()
    _handleBackPressed()
  }
  class WonderData {
    <<data>>
    historyInfo1 · historyInfo2
    constructionInfo1 · constructionInfo2
    locationInfo1 · locationInfo2
    pullQuote1Top · pullQuote1Bottom · pullQuote2
    callout1 · callout2
    videoId · lat · lng
  }
  class PopRouterOnOverScroll {
    <<widget>>
    controller
  }
  class GlobalCoordsBuilder {
    <<widget>>
    builder
  }
  class _SectionDividerState {
    <<widget state>>
    _isActivated
    _checkPosition()
    _getSwitchPt()
  }
  class _AnimatedCircleWithTextState {
    <<widget state>>
    _anim · _prevIndex
  }
  class _CollapsingPullQuoteImage {
    <<widget>>
    scrollPos
  }
  class _SlidingImageStack {
    <<widget>>
    scrollPos
  }
  class ScalingListItem {
    <<widget>>
    scrollPos
  }
  class _YouTubeThumbnail {
    <<widget>>
    id · imageUrl
  }
  class _MapsThumbnailState {
    <<widget state>>
    _mapFuture
    _loadGoogleMap()
  }
  class ScreenPaths {
    <<data>>
    video() · maps()
  }
  class FullscreenVideoViewer {
    <<page>>
    id
  }
  class AppLogic {
    <<logic>>
    supportedOrientationsOverride
  }
  WonderEditorialScreen --> _WonderEditorialScreenState : createState
  WonderEditorialScreen --> WonderData : data
  _WonderEditorialScreenState ..> PopRouterOnOverScroll : pops at 70 px overscroll
  _CollapsingPullQuoteImage ..> _WonderEditorialScreenState : listens to _scrollPos
  _SlidingImageStack ..> _WonderEditorialScreenState : listens to _scrollPos
  ScalingListItem ..> _WonderEditorialScreenState : listens to _scrollPos
  _SectionDividerState ..> _WonderEditorialScreenState : writes _sectionIndex
  _AnimatedCircleWithTextState ..> _WonderEditorialScreenState : spins on _sectionIndex
  _CollapsingPullQuoteImage ..> GlobalCoordsBuilder : y on screen
  _SlidingImageStack ..> GlobalCoordsBuilder : y on screen
  _SectionDividerState ..> GlobalCoordsBuilder : y on screen
  _YouTubeThumbnail ..> ScreenPaths : video()
  _MapsThumbnailState ..> ScreenPaths : maps()
  _YouTubeThumbnail ..> FullscreenVideoViewer : opens
  FullscreenVideoViewer ..> AppLogic : supportedOrientationsOverride
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

Illustration underneath, then four slivers: a transparent gap, the title block, the pinned arch app bar and the article column.

```mermaid
classDiagram
  direction LR
  class WonderEditorialScreen { <<page>> }
  class _TopIllustration { <<widget>> }
  class WonderIllustration { <<bg + mg, shortMode>> }
  class CustomScrollView { <<slivers>> }
  class _TitleText { <<widget>> }
  class WonderTitleText { <<hero title>> }
  class CompassDivider {
    <<widget>>
    isExpanded
  }
  class SliverAppBar { <<pinned>> }
  class _AppBar {
    <<widget>>
    _getArchType()
  }
  class ScalingListItem { <<widget>> }
  class _CircularTitleBar {
    <<widget>>
    titles · icons · index
  }
  class _AnimatedCircleWithText { <<widget>> }
  class _ScrollingContent { <<widget>> }
  class DropCapText { <<paragraph>> }
  class _CollapsingPullQuoteImage { <<widget>> }
  class _Callout { <<widget>> }
  class _SectionDivider { <<widget>> }
  class _YouTubeThumbnail { <<widget>> }
  class _SlidingImageStack { <<widget>> }
  class _LargeSimpleQuote { <<widget>> }
  class _MapsThumbnail { <<widget>> }
  class HiddenCollectible { <<widget>> }
  class BackBtn { <<north arrow>> }
  WonderEditorialScreen *-- _TopIllustration
  _TopIllustration *-- WonderIllustration
  WonderEditorialScreen *-- CustomScrollView
  WonderEditorialScreen *-- BackBtn
  CustomScrollView *-- _TitleText
  _TitleText *-- WonderTitleText
  _TitleText *-- CompassDivider
  CustomScrollView *-- SliverAppBar
  SliverAppBar *-- _AppBar
  _AppBar *-- ScalingListItem : arch-clipped photo 1
  _AppBar *-- _CircularTitleBar
  _CircularTitleBar *-- _AnimatedCircleWithText
  CustomScrollView *-- _ScrollingContent
  _ScrollingContent *-- DropCapText : x3
  _ScrollingContent *-- _CollapsingPullQuoteImage
  _ScrollingContent *-- _Callout : x2
  _ScrollingContent *-- _SectionDivider : x2
  _ScrollingContent *-- _YouTubeThumbnail
  _ScrollingContent *-- _SlidingImageStack
  _ScrollingContent *-- _LargeSimpleQuote
  _ScrollingContent *-- _MapsThumbnail
  _ScrollingContent *-- HiddenCollectible : 4 slots
  _SectionDivider *-- CompassDivider
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Which section the title shows · state machine {#state}

The circular title is driven by the two section dividers crossing the middle of the screen; each change spins the circle 180° in 600 ms.

```mermaid
stateDiagram-v2
  state "Facts and History (0)" as History
  state "Construction (1)" as Construction
  state "Location Info (2)" as Location
  [*] --> History
  History --> Construction : divider 1 rises above mid-screen
  Construction --> History : divider 1 drops below mid-screen
  Construction --> Location : divider 2 rises above mid-screen
  Location --> Construction : divider 2 drops below mid-screen
```

## Scroll down the story · sequence {#sequence}

A scroll tick becomes one notifier update; each listener measures itself and animates, and a divider crossing mid-screen flips the section.

```mermaid
sequenceDiagram
  actor User
  participant Scroll as ScrollController
  participant Editorial as _WonderEditorialScreenState
  participant TitleBlock as _TitleText
  participant Quote as _CollapsingPullQuoteImage
  participant Divider as _SectionDividerState
  participant Circle as _AnimatedCircleWithTextState
  participant Pop as _PopRouterOnOverScrollState
  User->>Scroll: drag up
  Scroll->>Editorial: _handleScrollChanged()
  Editorial->>Editorial: _scrollPos = pixels
  Editorial-->>TitleBlock: moves down 0.3 × pos, fades out by 500 px
  Editorial-->>Quote: GlobalCoordsBuilder y → collapse amount, quote halves meet
  Editorial-->>Divider: rebuild
  Divider->>Divider: _checkPosition(), y above half the screen?
  Divider->>Editorial: _sectionIndex = 1
  Editorial-->>Circle: didUpdateWidget() → spin 180°, Construction
  User->>Scroll: back at top, pull down 70 px
  Scroll->>Pop: _handleScrollChanged()
  Pop->>Pop: pointer still down → context.pop, back to Home
```

## Key files {#files}

- `lib/ui/screens/editorial/editorial_screen.dart` · scroll view and notifiers
- `lib/ui/screens/editorial/widgets/_scrolling_content.dart` · article order, video, map
- `lib/ui/screens/editorial/widgets/_app_bar.dart` · arch-clipped pinned header
- `lib/ui/screens/editorial/widgets/_circular_title_bar.dart` · rolling section title
- `lib/ui/screens/editorial/widgets/_section_divider.dart` · sets the section index
- `lib/ui/screens/editorial/widgets/_collapsing_pull_quote_image.dart` · collapsing pull quote
- `lib/ui/common/global_coords_builder.dart` · widget’s on-screen position
- `lib/ui/common/pop_router_on_over_scroll.dart` · pull past top to leave
- `lib/ui/common/modals/fullscreen_video_viewer.dart` · YouTube player
- `lib/ui/common/modals/fullscreen_maps_viewer.dart` · full-screen Google map
