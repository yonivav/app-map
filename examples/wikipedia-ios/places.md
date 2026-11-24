---
title: Places Module
sub: A map of articles about places around you, grouped into numbered clusters that split as you zoom, with a list view and place search.
card_title: Places
card: Map of nearby articles
screenshots:
- file: shots/places/01_map.jpg
  caption: Places asks for location before it shows nearby articles
---

## What it does {#what}

`PlacesViewController` shows an `MKMapView` of articles with coordinates. Without a query it runs the default search — **All top articles** in the visible region — and a search bar on top accepts a place name or a topic, with suggestions and recent place searches. `PlaceSearchService` turns a search into geosearch results from the wiki (or a fetch of saved articles with a location), and the results become `WMFArticle` rows in Core Data that a fetched-results controller watches. On the map the articles are grouped by quad key: the grouping precision follows the zoom, 4 levels finer than the visible span (capped at 17), and a group of 3 or more articles becomes one numbered `ArticlePlace` annotation that zooms in when tapped. Tapping a single article shows a popover card with its description, distance and bearing, save and share buttons, and opening it pushes the article. When you pan far enough from the last search, a **Redo search** button appears. A toggle switches to a list sorted by distance, and the user's location (if allowed) centres the map and orders the list.

## Logic · class diagram {#classes}

Searches write into Core Data; the map and list both read the same fetched results and regroup on every region change.

```mermaid
classDiagram
  direction LR
  class PlacesViewController {
    <<page>>
    currentSearch · articleFetchedResultsController
    performDefaultSearch()
    performSearch()
    updatePlaces()
    regroupArticlesIfNecessary()
    selectArticlePlace()
  }
  class ViewMode {
    <<enum>>
    map · list · search
    listOverlay · searchOverlay
  }
  class PlaceSearch {
    <<data>>
    type · origin · sortStyle
    string · region
  }
  class PlaceSearchType {
    <<enum>>
    text · location · nearby
  }
  class PlaceSearchService {
    <<service>>
    performSearch()
    fetchSavedArticles()
  }
  class LocationManager {
    <<service>>
    isAuthorized · location
    startMonitoringLocation()
  }
  class ArticlePlace {
    <<annotation>>
    articles · identifier
  }
  class WMFArticle { <<Core Data entity>> }
  PlacesViewController --> ViewMode : viewMode
  PlacesViewController --> PlaceSearch : currentSearch
  PlaceSearch --> PlaceSearchType : type
  PlacesViewController ..> PlaceSearchService : performSearch()
  PlacesViewController --> LocationManager : locationManager
  PlacesViewController o-- ArticlePlace : map annotations
  ArticlePlace o-- WMFArticle : articles
  PlaceSearchService ..> WMFArticle : saves results
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · view composition {#widgets}

```mermaid
classDiagram
  direction TB
  class PlacesViewController { <<page>> }
  class MapView { <<map>> }
  class ArticlePlaceView {
    <<annotation view>>
    annotation
  }
  class ArticlePopoverViewController { <<card>> }
  class PlaceSearchSuggestionController { <<suggestions>> }
  PlacesViewController *-- MapView
  MapView *-- ArticlePlaceView : one per group or article
  PlacesViewController *-- ArticlePopoverViewController : tap a place
  PlacesViewController *-- PlaceSearchSuggestionController : while searching
```

- `◆──` contains

## Open the map and an article · sequence {#sequence}

The default search runs as soon as the map has a region; regrouping follows every pan and zoom.

```mermaid
sequenceDiagram
  actor User
  participant Places as PlacesViewController
  participant Location as LocationManager
  participant Service as PlaceSearchService
  participant Popover as ArticlePopoverViewController
  participant Coord as ArticleCoordinator
  User->>Places: open the Places tab
  Places->>Location: startMonitoringLocation()
  Places->>Places: performDefaultSearch(), All top articles
  Places->>Service: performSearch()
  Service-->>Places: articles with coordinates, saved to Core Data
  Places->>Places: updatePlaces(), regroupArticlesIfNecessary()
  User->>Places: tap a numbered group
  Places->>Places: zooms in, groups split
  User->>Places: tap one article
  Places->>Places: selectArticlePlace()
  Places->>Popover: shows the card
  User->>Popover: tap Read
  Popover->>Places: didSelectAction read
  Places->>Coord: start(), pushes the article
```

## Key files {#files}

- `Wikipedia/Code/PlacesViewController.swift` · map, list, search, grouping
- `Wikipedia/Code/PlaceSearchService.swift` · geosearch and saved places
- `Wikipedia/Code/PlaceSearch.swift` · search kinds and origins
- `Wikipedia/Code/ArticlePlace.swift` · map annotation for one or more articles
- `Wikipedia/Code/ArticlePlaceView.swift` · annotation view
- `Wikipedia/Code/ArticlePopoverViewController.swift` · article card on the map
- `Wikipedia/Code/QuadKey.swift` · grouping by quad key
- `WMF Framework/LocationManager.swift` · location updates
