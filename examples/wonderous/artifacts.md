---
title: Artifacts Module
sub: 'The “artifacts” tab: a carousel of highlights, a search with a time-range filter, and a details page per Met Museum object.'
card_title: Artifacts
card: Highlights, search and Met Museum details
screenshots:
- file: shots/artifacts/01_carousel.jpg
  caption: Highlights carousel
- file: shots/artifacts/02_details.jpg
  caption: An artifact from the Met
- file: shots/artifacts/03_search.jpg
  caption: Search with the time-range filter
---

## What it does {#what}

The carousel shows the wonder’s highlight artifacts (6 per wonder, 5 for Christ the Redeemer — 47 Met Museum objects bundled in `HighlightData`) and loops. The centre item is a tall pill (1.5 × its width); neighbours shrink to circles and drop by 0.5 and 0.825 of the width, and items 3 or more away fade out. Item height is the screen height minus 200 minus the text area, clamped to 250–400 px, and the background is the current artifact blurred (sigma 6, no blur on Android) under a 60–80 % black veil. Tapping the centre opens `…/artifact/`; tapping a side item scrolls to it. “Browse all artifacts” and the search button open `…/search/`, which filters the wonder’s bundled `SearchData` (17 for Christ the Redeemer, 189–493 for the others, 2,686 in all): whole-word, case-insensitive matches on title or keywords, plural “s” allowed, with autocomplete from the wonder’s 11–103 suggestions (the first 10 when empty). A time-range panel, open or closed as last left (saved as `isSearchPanelOpen`), starts at the wonder’s artifact years, draws every result as a tick across −3000 to 2200 and filters the masonry grid (one column per 300 px). In Chinese a dismissible note says results are in English. Details load the object’s JSON from the wonderous.info mirror of the Met API through `ArtifactAPILogic`, which caches it by id; the image sits in an app bar that collapses from 50 % to 35 % of the screen (tap for a zoomable full-screen view) above six fields that slide in 100 ms apart after 600 ms.

## Logic · class diagram {#classes}

Highlights and search data ship inside the app; only the details page goes to the network, through a logic class that caches and a stateless service that parses.

```mermaid
classDiagram
  direction LR
  class _ArtifactScreenState {
    <<page state>>
    _artifacts · _currentPage · _currentArtifactIndex
    _handlePageChanged()
    _handleArtifactTap()
    _handleSearchTap()
  }
  class HighlightData {
    <<data>>
    title · date · artifactId
    imageUrl · imageUrlSmall
    forWonder()
  }
  class _ArtifactSearchScreenState {
    <<page state>>
    _query · _searchResults · _filteredResults
    _handleSearchSubmitted()
    _handleTimelineChanged()
    _updateResults()
    _updateFilter()
    _handleResultPressed()
  }
  class WonderData {
    <<data>>
    searchData · searchSuggestions
    artifactStartYr · artifactEndYr
  }
  class SearchData {
    <<data>>
    year · id · title · keywords
    imageUrlSmall
  }
  class PanelController {
    <<controller>>
    toggle()
  }
  class SearchVizController {
    <<controller>>
    value · minYear · maxYear
  }
  class SettingsLogic {
    <<logic>>
    isSearchPanelOpen
    hasDismissedSearchMessage
  }
  class _ArtifactDetailsScreenState {
    <<page state>>
    _future
  }
  class ArtifactAPILogic {
    <<logic>>
    _artifactCache
    getArtifactByID()
  }
  class ArtifactAPIService {
    <<service>>
    getSelfHostedObjectByID()
    getMetObjectByID()
    _parseArtifactData()
  }
  class HttpClient {
    <<service>>
    send()
  }
  class ServiceResult {
    <<data>>
    content · success
  }
  class ArtifactData {
    <<data>>
    title · date · period · country
    medium · dimension · classification · culture
    selfHostedImageUrl
  }
  _ArtifactScreenState o-- HighlightData : _artifacts
  _ArtifactScreenState ..> _ArtifactSearchScreenState : go search
  _ArtifactScreenState ..> _ArtifactDetailsScreenState : go artifact
  _ArtifactSearchScreenState ..> WonderData : searchData
  WonderData o-- SearchData : searchData
  _ArtifactSearchScreenState --> PanelController : panelController
  _ArtifactSearchScreenState --> SearchVizController : vizController
  _ArtifactSearchScreenState ..> SettingsLogic : isSearchPanelOpen
  _ArtifactSearchScreenState ..> _ArtifactDetailsScreenState : go artifact
  _ArtifactDetailsScreenState ..> ArtifactAPILogic : getArtifactByID()
  ArtifactAPILogic ..> ArtifactAPIService : getSelfHostedObjectByID()
  ArtifactAPIService ..> HttpClient : send()
  ArtifactAPIService ..> ServiceResult : wraps response
  ServiceResult --> ArtifactData : content
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

Three screens: the carousel tab, the search page with its expanding time-range panel, and the details page with a collapsing image.

```mermaid
classDiagram
  direction LR
  class ArtifactCarouselScreen { <<tab>> }
  class _BlurredImageBg { <<widget>> }
  class _CollapsingCarouselItem {
    <<widget>>
    indexOffset · width
  }
  class _DoubleBorderImage { <<widget>> }
  class _BottomTextContent { <<widget>> }
  class ArtifactSearchScreen { <<page>> }
  class _SearchInput { <<autocomplete>> }
  class _ResultsGrid { <<masonry grid>> }
  class _ResultTile { <<widget>> }
  class ExpandingTimeRangeSelector { <<widget>> }
  class _OpenedTimeRange { <<widget>> }
  class TimeRangePainter { <<result ticks>> }
  class RangeSelector { <<two handles>> }
  class WondersTimelineBuilder { <<wonder spans>> }
  class ArtifactDetailsScreen { <<page>> }
  class _ArtifactImageBtn { <<hero image>> }
  class _InfoColumn { <<widget>> }
  class _InfoRow {
    <<widget>>
    label · value
  }
  class HighlightData { <<data>> }
  class ArtifactData { <<data>> }
  ArtifactCarouselScreen *-- _BlurredImageBg
  ArtifactCarouselScreen *-- _CollapsingCarouselItem : PageView, looping
  _CollapsingCarouselItem *-- _DoubleBorderImage
  ArtifactCarouselScreen *-- _BottomTextContent
  _DoubleBorderImage --> HighlightData
  _BottomTextContent --> HighlightData
  ArtifactSearchScreen *-- _SearchInput
  ArtifactSearchScreen *-- _ResultsGrid
  _ResultsGrid *-- _ResultTile
  ArtifactSearchScreen *-- ExpandingTimeRangeSelector
  ExpandingTimeRangeSelector *-- _OpenedTimeRange : when open
  _OpenedTimeRange *-- TimeRangePainter
  _OpenedTimeRange *-- WondersTimelineBuilder
  _OpenedTimeRange *-- RangeSelector
  ArtifactDetailsScreen *-- _ArtifactImageBtn
  ArtifactDetailsScreen *-- _InfoColumn
  _InfoColumn *-- _InfoRow : x6
  _InfoColumn --> ArtifactData
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Search for an artifact and open it · sequence {#sequence}

Search is a local filter in two steps (query, then years); opening a result is the only network call.

```mermaid
sequenceDiagram
  actor User
  participant Carousel as _ArtifactScreenState
  participant Router as GoRouter
  participant Search as _ArtifactSearchScreenState
  participant Range as ExpandingTimeRangeSelector
  participant Artifact as _ArtifactDetailsScreenState
  participant Logic as ArtifactAPILogic
  participant Api as ArtifactAPIService
  User->>Carousel: Browse all artifacts → _handleSearchTap()
  Carousel->>Router: go …/search/type
  User->>Search: pick “coin” → _handleSearchSubmitted()
  Search->>Search: _updateResults(), whole-word match, plural allowed
  Search->>Search: _updateFilter(), keep results inside the years
  User->>Range: drag a handle
  Range->>Search: _handleTimelineChanged()
  User->>Search: tap a tile → _handleResultPressed()
  Search->>Router: go …/artifact/id
  Router->>Artifact: ArtifactDetailsScreen artifactId
  Artifact->>Logic: getArtifactByID() self-hosted
  Logic->>Api: getSelfHostedObjectByID()
  Api-->>Logic: ServiceResult with ArtifactData
  Logic-->>Artifact: cached by id, image and six fields animate in
```

## Key files {#files}

- `lib/ui/screens/artifact/artifact_carousel/` · highlights carousel
- `lib/ui/screens/artifact/artifact_search/artifact_search_screen.dart` · search, filter, controllers
- `lib/ui/screens/artifact/artifact_search/time_range_selector/` · year range panel
- `lib/ui/screens/artifact/artifact_details/` · details page
- `lib/logic/artifact_api_logic.dart` · cached artifact lookup
- `lib/logic/artifact_api_service.dart` · Met JSON → ArtifactData
- `lib/logic/common/http_client.dart` · GET, errors, ServiceResult
- `lib/logic/data/highlight_data.dart` · 47 highlight artifacts
- `lib/logic/data/wonders_data/search/` · bundled search data
