---
title: Places Module
sub: A MapLibre map of up to 75 nearby articles per request, clustered into numbered circles, with a list view and a link preview for each place.
card_title: Places
card: Map of nearby articles
screenshots:
- file: shots/places/01_map.jpg
  caption: 'Around the Eiffel Tower: nearby articles as markers'
- file: shots/places/02_preview.jpg
  caption: 'Tap a marker: the link preview with Read, Save and Share'
---

## What it does {#what}

Places opens from the **More** menu (or from a place card or an article's map action) as `PlacesActivity` with `PlacesFragment`. The map is MapLibre: on start it goes to the given location, or yours if location permission is granted, or the last one used, at zoom 15. Every time the camera stops, `onUpdateCameraPosition()` asks for new pages — unless the map is zoomed out past level 3, or it moved less than 20 % of the visible span and changed zoom by less than half a level since the last query. `PlacesFragmentViewModel` calls the wiki's geosearch API for up to 75 pages within the search radius, keeps only those with coordinates and sorts them by distance from you. Markers are drawn by a symbol manager with clustering: nearby markers merge into a numbered circle, and tapping a circle zooms in two levels over one second; at most 250 markers with thumbnails are cached. Tapping a marker magnifies it and opens a link preview with the article's summary and a button to read it. A toggle switches to a list sorted by distance, the search bar searches places by name, and a filter picks which wiki's articles to show.

## Logic · class diagram {#classes}

The fragment owns the map and decides when to fetch; the view model only fetches and sorts.

```mermaid
classDiagram
  direction LR
  class PlacesActivity {
    <<activity>>
    newIntent()
  }
  class PlacesFragment {
    <<page>>
    ITEMS_PER_REQUEST · MAX_ANNOTATIONS
    onUpdateCameraPosition()
    updateMapMarkers()
    setUpSymbolManagerWithClustering()
    onMapClick()
    showLinkPreview()
    goToLocation()
  }
  class PlacesFragmentViewModel {
    <<view-model>>
    wikiSite · lastKnownLocation
    nearbyPagesLiveData
    fetchNearbyPages()
  }
  class NearbyPage {
    <<data>>
    pageId · pageTitle · latitude · longitude
  }
  class ServiceFactory {
    <<network>>
    get()
  }
  class LinkPreviewDialog { <<bottom sheet>> }
  class PlacesFilterActivity { <<activity>> }
  PlacesActivity *-- PlacesFragment
  PlacesFragment --> PlacesFragmentViewModel : viewModel
  PlacesFragmentViewModel ..> ServiceFactory : geosearch
  PlacesFragmentViewModel o-- NearbyPage : nearbyPagesLiveData
  PlacesFragment ..> LinkPreviewDialog : tap a marker
  PlacesFragment ..> PlacesFilterActivity : choose the wiki
```

- `──▷` holds
- `◆──` contains
- `◇──` list of
- `┄┄▷` uses · opens

## Pan the map and open a place · sequence {#sequence}

A fetch happens only when the camera settles somewhere new enough.

```mermaid
sequenceDiagram
  actor User
  participant Map as PlacesFragment
  participant Model as PlacesFragmentViewModel
  participant Api as ServiceFactory
  participant Preview as LinkPreviewDialog
  User->>Map: pan to a new area
  Map->>Map: onUpdateCameraPosition()
  Note over Map: skipped below zoom 3 or if it moved less than 20 %
  Map->>Model: fetchNearbyPages(lat, lon, radius, 75)
  Model->>Api: geosearch around the centre
  Api-->>Model: pages with coordinates
  Model-->>Map: nearbyPagesLiveData, sorted by distance
  Map->>Map: updateMapMarkers(), clusters
  User->>Map: tap a marker
  Map->>Map: showLinkPreview()
  Map->>Preview: shows the summary
  User->>Preview: tap Read
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/places/PlacesFragment.kt` · map, markers, clusters, list
- `app/src/main/java/org/wikipedia/places/PlacesFragmentViewModel.kt` · geosearch
- `app/src/main/java/org/wikipedia/places/PlacesActivity.kt` · activity and intents
- `app/src/main/java/org/wikipedia/places/PlacesFilterActivity.kt` · wiki filter
- `app/src/main/java/org/wikipedia/dataclient/page/NearbyPage.kt` · a place on the map
