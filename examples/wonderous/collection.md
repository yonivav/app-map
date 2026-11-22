---
title: Collection Module
sub: 'A treasure hunt: 24 artifacts hidden around the wonders’ tabs, a celebration when you find one, and a collection to keep them in.'
card_title: Collection
card: 24 hidden artifacts to find and keep
screenshots:
- file: shots/collection/01_collection.jpg
  caption: Collection, before any find
- file: shots/collection/02_scrolled.jpg
  caption: Three tiles per wonder, 24 in all
---

## What it does {#what}

`collectiblesData` holds 24 collectibles, 3 per wonder, each a Met Museum object with an icon. A wonder’s first is hidden in its editorial, the second in a corner cell of its photo grid and the third at the end of its events list. The icon shimmers, shakes and pulses on a loop; tapping it opens “Artifact Discovered” as a fade dialog — the icon flies in as a hero and grows from 1.5× to 3×, at 1,050 ms the screen swaps to the artifact image, a ribbon, its title and culture, with particles — and 200 ms later the collectible becomes discovered, so the hidden icon folds away. Each state is saved in `collectibles.dat` (at most every 2 s). On iOS every change also updates the home-screen widget: the found count and the last find’s title, date (fetched through `ArtifactAPILogic`) and image as base64. “view in my collection” opens `…/collection?id=` scrolled to that wonder. The collection lists the 8 wonders (300 px cards, or 600 px side by side in landscape) with three tiles each: dark silhouettes for lost, an orange border and glow for newly discovered. An “N new items” bar jumps to the first new one, and the footer shows the share found and “count of 24” with a bar that fills in 1.5 s. Opening a found item goes to its artifact page and marks it explored 300 ms later. A reset button (with confirmation) exists only in debug builds.

## Logic · class diagram {#classes}

CollectiblesLogic is the single source of truth: a ValueNotifier map of id → state that every hidden icon, the collection and the home-screen widget follow.

```mermaid
classDiagram
  direction LR
  class CollectiblesLogic {
    <<logic>>
    all · statesById
    discoveredCount · exploredCount
    forWonder() · fromId()
    isLost()
    getFirstDiscoveredOrNull()
    setState()
    reset()
    _updateCounts()
    _updateNativeHomeWidgetData()
  }
  class CollectibleData {
    <<data>>
    title · artifactId · wonder · icon
    imageUrl · imageUrlSmall · subtitle
  }
  class CollectibleState {
    <<state>>
    lost · discovered · explored
  }
  class ThrottledSaveLoadMixin {
    <<mixin>>
    scheduleSave()
  }
  class NativeWidgetService {
    <<service>>
    isSupported
    save()
    markDirty()
  }
  class ArtifactAPILogic {
    <<logic>>
    getArtifactByID()
  }
  class HiddenCollectible {
    <<widget>>
    index · matches
  }
  class CollectibleItem {
    <<widget>>
    collectible
    _handleTap()
  }
  class CollectibleFoundScreen {
    <<modal>>
    collectible · imageProvider
    _handleViewCollectionPressed()
  }
  class _CollectionScreenState {
    <<page state>>
    _scrollToTarget()
    _handleReset()
  }
  class _CollectionListCard {
    <<widget>>
    _showDetails()
  }
  ThrottledSaveLoadMixin <|-- CollectiblesLogic
  CollectiblesLogic o-- CollectibleData : all
  CollectiblesLogic ..> CollectibleState : statesById values
  CollectiblesLogic --> NativeWidgetService : _nativeWidget
  CollectiblesLogic ..> ArtifactAPILogic : getArtifactByID()
  HiddenCollectible ..> CollectiblesLogic : forWonder()
  HiddenCollectible *-- CollectibleItem
  CollectibleItem ..> CollectibleFoundScreen : opens
  CollectibleItem ..> CollectiblesLogic : setState()
  CollectibleFoundScreen ..> _CollectionScreenState : go collection?id
  _CollectionScreenState ..> CollectiblesLogic : reset()
  _CollectionListCard ..> CollectiblesLogic : setState()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

The collection is a header, a “new items” bar, a list of one card per wonder with three tiles each, and a progress footer.

```mermaid
classDiagram
  direction TB
  class CollectionScreen {
    <<page>>
    fromId
  }
  class AppHeader { <<Collection>> }
  class _NewlyDiscoveredItemsBtn {
    <<widget>>
    count
  }
  class _CollectionList {
    <<widget>>
    fromId · scrollKey
  }
  class _CollectionListCard {
    <<widget>>
    data · fromId
  }
  class _CollectibleImage {
    <<widget>>
    collectible · state · heroTag
  }
  class _CollectionFooter {
    <<widget>>
    count · total
  }
  class CollectibleFoundScreen { <<modal>> }
  class _AnimatedRibbon { <<widget>> }
  class _CelebrationParticles { <<widget>> }
  class CollectibleData { <<data>> }
  CollectionScreen *-- AppHeader
  CollectionScreen *-- _NewlyDiscoveredItemsBtn
  CollectionScreen *-- _CollectionList
  _CollectionList *-- _CollectionListCard : 8 wonders
  _CollectionListCard *-- _CollectibleImage : x3
  _CollectibleImage --> CollectibleData
  CollectionScreen *-- _CollectionFooter
  CollectibleFoundScreen *-- _CelebrationParticles
  CollectibleFoundScreen *-- _AnimatedRibbon
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## A collectible’s life · state machine {#state}

Stored per id in CollectiblesLogic.statesById and saved to collectibles.dat; only a debug reset goes backwards.

```mermaid
stateDiagram-v2
  state "lost (0)" as Lost
  state "discovered (1)" as Discovered
  state "explored (2)" as Explored
  [*] --> Lost
  Lost --> Discovered : tap the hidden icon, after 200 ms
  Discovered --> Explored : open it from the collection, after 300 ms
  Discovered --> Lost : debug reset
  Explored --> Lost : debug reset
```

## Find a hidden artifact and look at it · sequence {#sequence}

The celebration and the state change run side by side; everything else reacts to the new state.

```mermaid
sequenceDiagram
  actor User
  participant Item as CollectibleItem
  participant App as AppLogic
  participant Found as CollectibleFoundScreen
  participant Logic as CollectiblesLogic
  participant Widget as NativeWidgetService
  participant Router as GoRouter
  participant Collection as _CollectionScreenState
  participant Card as _CollectionListCard
  User->>Item: tap the shimmering icon → _handleTap()
  Item->>App: showFullscreenDialogRoute()
  App->>Found: hero icon grows, swaps to the reveal at 1,050 ms
  Item->>Logic: setState() discovered, after 200 ms
  Logic->>Logic: _updateCounts(), scheduleSave()
  Logic->>Widget: save() count and last find, markDirty()
  User->>Found: view in my collection → _handleViewCollectionPressed()
  Found->>Router: pop, go …/collection?id=artifactId
  Router->>Collection: _scrollToTarget(), that wonder’s card
  User->>Card: tap the new tile → _showDetails()
  Card->>Router: go …/artifact/id
  Card->>Logic: setState() explored, after 300 ms
```

## Key files {#files}

- `lib/logic/collectibles_logic.dart` · states, counts, widget data
- `lib/logic/data/collectible_data.dart` · 24 collectibles, states
- `lib/logic/native_widget_service.dart` · iOS home-screen widget
- `lib/ui/common/hidden_collectible.dart` · picks this wonder’s item
- `lib/ui/common/collectible_item.dart` · shimmering icon, tap
- `lib/ui/screens/collectible_found/` · discovery celebration
- `lib/ui/screens/collection/` · collection list and footer
