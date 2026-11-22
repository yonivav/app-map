---
title: Photo Gallery Module
sub: 'The “photo gallery” tab: a 5 × 5 wall of photos you move across one cell at a time, with a full-screen viewer.'
card_title: Photo Gallery
card: Swipeable 5 × 5 wall of photos
screenshots:
- file: shots/photo-gallery/01_grid.jpg
  caption: The swipe grid with the cut-out photo
---

## What it does {#what}

The wonder’s Unsplash collection id picks one of 8 bundled lists of 24 photo ids (`UnsplashPhotoData.photosByCollectionId`); the list is repeated and cut to fill 25 cells, and each photo loads from wonderous.info at 400, 800 or 1200 px (doubled on 1.5× screens and desktop) — the live Unsplash API in `UnsplashService` is only used by dev tools. The grid starts on index 13 (12.5 rounds up, one cell right of centre). A swipe of 30 px in any of 8 directions or an arrow key moves one cell or row (never past an edge), and tapping a visible neighbour selects it; the whole grid slides there in 240 ms while the selected photo scales to 1.15 and a 70 % black overlay keeps a rounded cut-out around it that briefly shrinks 25 % along the swipe axis. Tapping the selected photo opens `FullscreenUrlImgViewer` with all 25 at 1200 px (pinch to zoom, swipe between them); closing it returns the page you ended on and the grid jumps there without animating. One corner cell, chosen per wonder, hides the wonder’s second collectible until it is found.

## Logic · class diagram {#classes}

Everything is index arithmetic on a fixed grid: swipes, keys and taps become a new index, and the offset that centres it is computed, not scrolled.

```mermaid
classDiagram
  direction LR
  class PhotoGallery {
    <<page>>
    collectionId · wonderType
  }
  class _PhotoGalleryState {
    <<page state>>
    _gridSize · _index · _photoIds · _lastSwipeDir
    _initPhotoIds()
    _handleSwipe()
    _handleKeyDown()
    _handleImageTapped()
    _setIndex()
    _calculateCurrentOffset()
    _getCollectibleIndex()
    _checkCollectibleIndex()
  }
  class EightWaySwipeDetector {
    <<widget>>
    threshold
    onSwipe
  }
  class UnsplashLogic {
    <<logic>>
    getCollectionPhotos()
  }
  class UnsplashPhotoData {
    <<data>>
    photosByCollectionId
    getSelfHostedUrl()
  }
  class UnsplashPhotoSize { <<enum>> }
  class CollectiblesLogic {
    <<logic>>
    statesById
    isLost()
  }
  class AppLogic {
    <<logic>>
    showFullscreenDialogRoute()
  }
  class FullscreenUrlImgViewer {
    <<modal>>
    urls · index
    imageScale
  }
  PhotoGallery --> _PhotoGalleryState : createState
  EightWaySwipeDetector ..> _PhotoGalleryState : onSwipe → _handleSwipe()
  _PhotoGalleryState ..> UnsplashLogic : getCollectionPhotos()
  UnsplashLogic ..> UnsplashPhotoData : photosByCollectionId
  _PhotoGalleryState ..> UnsplashPhotoData : getSelfHostedUrl()
  UnsplashPhotoData ..> UnsplashPhotoSize : med · large · xl
  _PhotoGalleryState ..> CollectiblesLogic : isLost()
  _PhotoGalleryState ..> AppLogic : showFullscreenDialogRoute()
  AppLogic ..> FullscreenUrlImgViewer : returns last page
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

A grid bigger than the screen, translated so the selected cell sits in the middle, under a black overlay with a cut-out.

```mermaid
classDiagram
  direction TB
  class PhotoGallery { <<page>> }
  class FullscreenKeyboardListener { <<arrow keys>> }
  class AppLoadingIndicator { <<while empty>> }
  class _AnimatedCutoutOverlay {
    <<widget>>
    cutoutSize · swipeDir · opacity
  }
  class _CutoutClipper { <<clipper>> }
  class EightWaySwipeDetector { <<widget>> }
  class GridView { <<25 cells>> }
  class UnsplashPhoto {
    <<widget>>
    id · size
  }
  class AppImage { <<network image>> }
  class HiddenCollectible { <<one cell>> }
  PhotoGallery *-- FullscreenKeyboardListener
  FullscreenKeyboardListener *-- AppLoadingIndicator
  FullscreenKeyboardListener *-- _AnimatedCutoutOverlay
  _AnimatedCutoutOverlay *-- _CutoutClipper
  _AnimatedCutoutOverlay *-- EightWaySwipeDetector
  EightWaySwipeDetector *-- GridView : slides via TweenAnimationBuilder
  GridView *-- UnsplashPhoto : 25 cells
  GridView *-- HiddenCollectible : 1 cell until found
  UnsplashPhoto *-- AppImage
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Swipe across the wall and open a photo · sequence {#sequence}

A swipe is snapped to one of 8 directions, turned into an index, and the grid animates to that index’s offset.

```mermaid
sequenceDiagram
  actor User
  participant Swipe as EightWaySwipeDetector
  participant Gallery as _PhotoGalleryState
  participant Overlay as _AnimatedCutoutOverlay
  participant Photo as UnsplashPhotoData
  participant App as AppLogic
  participant Viewer as FullscreenUrlImgViewer
  User->>Swipe: drag 30 px up-left
  Swipe->>Swipe: snap to an 8-way direction
  Swipe->>Gallery: _handleSwipe()
  Gallery->>Gallery: index ± 1 and ± 5, stop at edges
  Gallery->>Gallery: _setIndex(), focus that cell
  Gallery->>Gallery: _calculateCurrentOffset(), grid slides 240 ms
  Gallery-->>Overlay: new key → cut-out shrinks and springs back
  User->>Gallery: tap the selected photo → _handleImageTapped()
  Gallery->>Photo: getSelfHostedUrl() xl, for all 25
  Gallery->>App: showFullscreenDialogRoute()
  App->>Viewer: swipe and pinch-zoom the photos
  Viewer-->>Gallery: pops with the page it ended on
  Gallery->>Gallery: _setIndex() without animation
```

## Key files {#files}

- `lib/ui/screens/photo_gallery/photo_gallery.dart` · grid, index math, taps
- `lib/ui/screens/photo_gallery/widgets/_animated_cutout_overlay.dart` · overlay with cut-out
- `lib/ui/common/controls/eight_way_swipe_detector.dart` · 8-direction swipes
- `lib/ui/common/modals/fullscreen_url_img_viewer.dart` · full-screen photo pager
- `lib/logic/unsplash_logic.dart` · photo ids per collection
- `lib/logic/data/unsplash_photo_data.dart` · bundled ids, image URLs
