---
title: Timeline Module
sub: 'The Global Timeline: all eight wonders and 51 world events on one zoomable, scrubbable scroll from 3000 BCE to 2200 CE.'
card_title: Timeline
card: Zoomable 5,200-year global timeline
screenshots:
- file: shots/timeline/01_timeline.jpg
  caption: Global timeline settled on Machu Picchu
---

## What it does {#what}

Opened from the menu or a wonder’s events tab with `?type=`, it scrolls a vertical timeline of 5,200 years (`WondersLogic.timelineStartYear` −3000 to `timelineEndYear` 2200). The content height runs from 1,200 px minus half the viewport to 5,500 px with zoom (0–1, starting at 0.5); pinching (Ctrl + wheel on desktop) zooms while keeping the current year in place, and so does resizing the window. Year markers step every 500, 250 or 100 years as the content grows past 800 and 1,500 px. The 8 wonders sit on 3 non-overlapping tracks, each at least 100 px long, and each one’s image slides along its span as the centre year passes it; wonders other than the chosen one are greyed. A dashed centre line shows the year, the era below it changes at −600, 476 and 1450 (Prehistory, Classical, Early Modern, Modern), and on open the view jumps 200 px short of the wonder’s start year and glides there in 1.3 s. `TimelineLogic.events` holds 43 global events plus one “construction begins” event per wonder; the dot within 10 px of the centre line grows from 2 to 6 px with a haptic tick, and its card pops in after a 500 ms debounce. Tapping a dot scrolls to it. The 80 px scrubber at the bottom shares the same `ScrollController`: its box shows the visible part and dragging it scrolls the main view.

## Logic · class diagram {#classes}

A shared ScrollController is the timeline’s only clock: a small controller turns pixels into years and back, and the markers, era text and scrubber all read from it.

```mermaid
classDiagram
  direction LR
  class TimelineScreen {
    <<page>>
    type
  }
  class _TimelineScreenState {
    <<page state>>
    _scroller · _year
    _handleViewportYearChanged()
  }
  class _ScalingViewportState {
    <<widget state>>
    controller · _currentEventMarker
    _handleEventMarkerChanged()
    _handleMarkerPressed()
  }
  class _ScrollingViewportController {
    <<controller>>
    _zoom · _currentYr
    init()
    setZoom()
    jumpToYear()
    calculateContentHeight()
    calculateYearFromScrollPos()
    calculateScrollPosFromYear()
    _handleScaleUpdate()
  }
  class ScrollController { <<shared>> }
  class _BottomScrubber {
    <<widget>>
    _calculateScrollFraction()
    _calculateViewPortFraction()
  }
  class _EventMarkersState {
    <<widget state>>
    selectedEvent
    _updateSelectedEvent()
  }
  class _EventPopupsState {
    <<widget state>>
    _eventToShow
    showCardForCurrentYr()
  }
  class Debouncer {
    <<data>>
    interval
    call()
  }
  class TimelineLogic {
    <<logic>>
    events
    init()
  }
  class TimelineEvent {
    <<data>>
    year · description
  }
  class GlobalEventsData {
    <<data>>
    globalEvents
  }
  class WondersLogic {
    <<logic>>
    all
    timelineStartYear · timelineEndYear
  }
  TimelineScreen --> _TimelineScreenState : createState
  _TimelineScreenState --> ScrollController : _scroller
  _ScalingViewportState --> _ScrollingViewportController : controller
  _ScrollingViewportController ..> ScrollController : jumps and animates
  _BottomScrubber ..> ScrollController : drags position
  _ScrollingViewportController ..> _TimelineScreenState : onYearChanged → _handleViewportYearChanged()
  _ScrollingViewportController ..> WondersLogic : timelineStartYear · timelineEndYear
  _EventMarkersState ..> TimelineLogic : events
  _EventMarkersState ..> _ScalingViewportState : _handleEventMarkerChanged()
  _ScalingViewportState ..> _EventPopupsState : _currentEventMarker
  _EventPopupsState --> Debouncer : _debouncer
  TimelineLogic o-- TimelineEvent : events
  TimelineLogic ..> GlobalEventsData : globalEvents
  TimelineLogic ..> WondersLogic : all
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

Header, the zoomable viewport (year markers, wonder tracks, event dots, centre line, popup), the era label and the mini scrubber.

```mermaid
classDiagram
  direction TB
  class TimelineScreen { <<page>> }
  class AppHeader { <<Global Timeline>> }
  class _ScrollingViewport {
    <<widget>>
    minSize · maxSize
  }
  class _YearMarkers { <<widget>> }
  class WondersTimelineBuilder {
    <<widget>>
    axis · minSize
  }
  class TimelineSection {
    <<widget>>
    data · selectedYr
  }
  class _EventMarkers { <<widget>> }
  class _EventMarker {
    <<widget>>
    isSelected
  }
  class _DashedDividerWithYear { <<centre line>> }
  class _EventPopups { <<widget>> }
  class TimelineEventCard { <<widget>> }
  class _AnimatedEraText { <<widget>> }
  class _BottomScrubber { <<widget>> }
  class WonderData { <<data>> }
  TimelineScreen *-- AppHeader
  TimelineScreen *-- _ScrollingViewport
  _ScrollingViewport *-- _YearMarkers
  _ScrollingViewport *-- WondersTimelineBuilder : vertical
  WondersTimelineBuilder *-- TimelineSection : one per wonder
  TimelineSection --> WonderData
  _ScrollingViewport *-- _EventMarkers
  _EventMarkers *-- _EventMarker : one per event
  _ScrollingViewport *-- _DashedDividerWithYear
  _ScrollingViewport *-- _EventPopups
  _EventPopups *-- TimelineEventCard
  TimelineScreen *-- _AnimatedEraText
  TimelineScreen *-- _BottomScrubber
  _BottomScrubber *-- WondersTimelineBuilder : horizontal mini
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Open the timeline at a wonder and browse events · sequence {#sequence}

Every change of scroll position is turned back into a year, and everything else follows from that year.

```mermaid
sequenceDiagram
  actor User
  participant Screen as _TimelineScreenState
  participant View as _ScalingViewportState
  participant Ctrl as _ScrollingViewportController
  participant Scroll as ScrollController
  participant Markers as _EventMarkersState
  participant Popup as _EventPopupsState
  View->>Ctrl: init()
  Ctrl->>Ctrl: setZoom() at 0.5
  Ctrl->>Ctrl: calculateScrollPosFromYear() of the wonder’s start
  Ctrl->>Scroll: jump 200 px short, glide 1.3 s
  User->>Scroll: scroll or pinch
  Scroll->>Ctrl: _updateCurrentYear()
  Ctrl->>Screen: _handleViewportYearChanged() → era text
  Scroll-->>Markers: rebuild with the centre year
  Markers->>Markers: _updateSelectedEvent(), dot within 10 px
  Markers->>View: _handleEventMarkerChanged(), haptic
  View->>Popup: currentEvent
  Popup->>Popup: Debouncer 500 ms → showCardForCurrentYr()
  User->>View: tap a dot → _handleMarkerPressed()
  View->>Scroll: animate to that year, 600 ms
```

## Key files {#files}

- `lib/ui/screens/timeline/timeline_screen.dart` · layout, shared scroller
- `lib/ui/screens/timeline/widgets/_scrolling_viewport.dart` · zoomable timeline
- `lib/ui/screens/timeline/widgets/_scrolling_viewport_controller.dart` · years ↔ pixels, zoom
- `lib/ui/screens/timeline/widgets/_event_markers.dart` · event dots, selection
- `lib/ui/screens/timeline/widgets/_event_popups.dart` · debounced event card
- `lib/ui/screens/timeline/widgets/_bottom_scrubber.dart` · mini timeline scrubber
- `lib/logic/timeline_logic.dart` · global + wonder events
- `lib/logic/data/timeline_data.dart` · 43 global events
