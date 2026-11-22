---
title: Wonderous App Map
sub: How the app works, one module at a time · **tap a module or a box** to open its map
modules:
- splash
- intro
- home
- home-menu
- wonder-details
- editorial
- photo-gallery
- artifacts
- events
- timeline
- collection
links:
  screens:
    SplashN: splash
    IntroN: intro
    HomeN: home
    MenuN: home-menu
    AboutN: home-menu
    DetailsN: wonder-details
    EditorialN: editorial
    VideoN: editorial
    MapsN: editorial
    GalleryN: photo-gallery
    ViewerN: photo-gallery
    CarouselN: artifacts
    SearchN: artifacts
    ArtifactN: artifacts
    EventsN: events
    TimelineN: timeline
    FoundN: collection
    CollectionN: collection
  services:
    SplashS: splash
    IntroS: intro
    HomeS: home
    MenuS: home-menu
    DetailsS: wonder-details
    EditorialS: editorial
    GalleryS: photo-gallery
    ArtifactsS: artifacts
    EventsS: events
    TimelineS: timeline
    CollectionS: collection
---

## Screens · how the user moves

Every screen is a GoRouter path under one ShellRoute: the app boots on a hidden `/`, goes to `/welcome` once and then lives under `/home`. A wonder opens at `/home/wonder/?t=`, and search, artifact, video, map, timeline and collection pages are appended to the current path, so back always returns where you came from.

```mermaid
flowchart TB
  subgraph splash [Splash]
    SplashN["Splash /<br/>WondersApp"]
  end
  subgraph intro [Intro]
    IntroN["Intro /welcome<br/>IntroScreen"]
  end
  subgraph home [Home]
    HomeN["Home /home<br/>HomeScreen"]
  end
  subgraph menu [Home Menu]
    MenuN["Menu<br/>HomeMenu"]
    AboutN["About<br/>AboutDialogContent"]
  end
  subgraph details [Wonder Details]
    DetailsN["Wonder /home/wonder/type<br/>WonderDetailsScreen"]
  end
  subgraph editorial [Editorial]
    EditorialN["Information & history<br/>WonderEditorialScreen"]
    VideoN["Video<br/>FullscreenVideoViewer"]
    MapsN["Map<br/>FullscreenMapsViewer"]
  end
  subgraph gallery [Photo Gallery]
    GalleryN["Photo gallery<br/>PhotoGallery"]
    ViewerN["Full-screen photo<br/>FullscreenUrlImgViewer"]
  end
  subgraph artifacts [Artifacts]
    CarouselN["Highlights<br/>ArtifactCarouselScreen"]
    SearchN["Browse artifacts<br/>ArtifactSearchScreen"]
    ArtifactN["Artifact<br/>ArtifactDetailsScreen"]
  end
  subgraph events [Events]
    EventsN["Events<br/>WonderEvents"]
  end
  subgraph timeline [Timeline]
    TimelineN["Global timeline<br/>TimelineScreen"]
  end
  subgraph collection [Collection]
    FoundN["Artifact discovered<br/>CollectibleFoundScreen"]
    CollectionN["Collection<br/>CollectionScreen"]
  end
  SplashN -->|first run| IntroN
  SplashN -->|onboarded, or deep link| HomeN
  IntroN -->|finish| HomeN
  HomeN -->|menu button| MenuN
  MenuN --> AboutN
  MenuN -->|Explore the timeline| TimelineN
  MenuN -->|View your collection| CollectionN
  HomeN -->|swipe up| DetailsN
  DetailsN -->|tab 0| EditorialN
  DetailsN -->|tab 1| GalleryN
  DetailsN -->|tab 2| CarouselN
  DetailsN -->|tab 3| EventsN
  EditorialN --> VideoN
  EditorialN --> MapsN
  GalleryN --> ViewerN
  CarouselN -->|Browse all artifacts| SearchN
  CarouselN -->|tap centre| ArtifactN
  SearchN -->|tap result| ArtifactN
  EventsN -->|Open global timeline| TimelineN
  EditorialN -->|hidden icon| FoundN
  GalleryN -->|hidden icon| FoundN
  EventsN -->|hidden icon| FoundN
  FoundN -->|view in my collection| CollectionN
  CollectionN -->|found item| ArtifactN
```

- `───▷` opens
- `▭` tap to open its module

## Services · what the screens talk through

The logic layer is a set of plain classes registered as lazy singletons in get_it and reached through top-level getters (`wondersLogic`, `settingsLogic`…). Content ships with the app; only artifact details (and their images) come from the network, and only settings and collectibles are saved.

```mermaid
flowchart LR
  subgraph Screens
    SplashS["Splash"]
    IntroS["Intro"]
    HomeS["Home"]
    MenuS["Home Menu"]
    DetailsS["Wonder Details"]
    EditorialS["Editorial"]
    GalleryS["Photo Gallery"]
    ArtifactsS["Artifacts"]
    EventsS["Events"]
    TimelineS["Timeline"]
    CollectionS["Collection"]
  end
  subgraph Logic ["get_it singletons"]
    AppL["AppLogic"]
    SettingsL["SettingsLogic"]
    LocaleL["LocaleLogic"]
    WondersL["WondersLogic"]
    TimelineL["TimelineLogic"]
    CollectL["CollectiblesLogic"]
    UnsplashL["UnsplashLogic"]
    ArtifactL["ArtifactAPILogic"]
    ArtifactSvc["ArtifactAPIService"]
    NativeSvc["NativeWidgetService"]
  end
  subgraph Infra ["storage and network"]
    PrefsF["JsonPrefsFile"]
    HttpC["HttpClient"]
  end
  SplashS -->|bootstrap| AppL
  IntroS -->|hasCompletedOnboarding| SettingsL
  HomeS -->|all| WondersL
  HomeS -->|prevWonderIndex| SettingsL
  HomeS -->|showFullscreenDialogRoute| AppL
  MenuS -->|changeLocale| SettingsL
  DetailsS -->|getData| WondersL
  DetailsS -->|shouldUseNavRail| AppL
  EditorialS -->|forWonder| CollectL
  GalleryS -->|getCollectionPhotos| UnsplashL
  GalleryS -->|isLost| CollectL
  ArtifactsS -->|getArtifactByID| ArtifactL
  ArtifactsS -->|isSearchPanelOpen| SettingsL
  EventsS -->|getData| WondersL
  TimelineS -->|events| TimelineL
  CollectionS -->|setState| CollectL
  AppL -->|load| SettingsL
  AppL -->|load| LocaleL
  AppL -->|init| TimelineL
  SettingsL -->|loadIfChanged| LocaleL
  ArtifactL -->|getSelfHostedObjectByID| ArtifactSvc
  ArtifactSvc -->|send| HttpC
  CollectL -->|save, markDirty| NativeSvc
  CollectL -->|getArtifactByID| ArtifactL
  SettingsL -->|scheduleSave| PrefsF
  CollectL -->|scheduleSave| PrefsF
```

- `───▷` calls, labelled with the method
- `▭` tap to open its module
