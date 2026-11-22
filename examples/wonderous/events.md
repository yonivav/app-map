---
title: Events Module
sub: 'The “events” tab: six dated moments in the wonder’s history, scrolling over its picture and place in time.'
card_title: Events
card: Six dated moments per wonder
screenshots:
- file: shots/events/01_events.jpg
  caption: Events over the wonder and mini timeline
- file: shots/events/02_scrolled.jpg
  caption: Later events
---

## What it does {#what}

Each wonder carries 6 events (`WonderData.events`, year → text). They appear as dark cards that fade in over 900 ms and slide up with a small overshoot, 100 ms apart. In portrait the list scrolls over the top 55 % of the screen (at least 200 px), which shows the wonder’s flattened image, its title, a mini timeline of all 8 wonders on 3 non-overlapping tracks with this one filled in, and its dates and era; the background blurs and darkens (up to 60 %) between 50 and 350 px of scroll. On wide screens — aspect ratio over 0.85 on phones, so foldables count, or over 1 elsewhere — the image and list sit side by side, and the scroll offset carries over when the layout switches. The third hidden collectible waits at the end of the list. “Open global timeline” (button and header icon) goes to `…/timeline?type=`.

## Logic · class diagram {#classes}

A read-only view over WonderData: the only state is the scroll offset, kept so the two layouts can hand it to each other.

```mermaid
classDiagram
  direction LR
  class WonderEvents {
    <<page>>
    type · contentPadding
  }
  class _WonderEventsState {
    <<page state>>
    _data · _scrollPos
    _handleScroll()
    _buildSingleColumn()
    _buildTwoColumn()
  }
  class _EventsListState {
    <<widget state>>
    _scroller
    _buildScrollingList()
    _buildScrollingListWithBlur()
  }
  class WondersLogic {
    <<logic>>
    getData()
  }
  class WonderData {
    <<data>>
    events · startYr · endYr
  }
  class ScreenPaths {
    <<data>>
    timeline()
  }
  WonderEvents --> _WonderEventsState : createState
  _WonderEventsState ..> WondersLogic : getData()
  WondersLogic o-- WonderData : all
  _WonderEventsState --> _EventsListState : _eventsListKey
  _EventsListState ..> _WonderEventsState : onScroll → _handleScroll()
  _EventsListState ..> WonderData : events
  _WonderEventsState ..> ScreenPaths : timeline()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses
- `──▷|` extends

## Screen · widget composition {#widgets}

Portrait stacks the list over the image-with-timeline; landscape puts them in a row.

```mermaid
classDiagram
  direction TB
  class WonderEvents { <<page>> }
  class AppHeader { <<timeline icon>> }
  class _WonderImageWithTimeline {
    <<widget>>
    data · height
  }
  class WonderTitleText { <<widget>> }
  class WondersTimelineBuilder {
    <<widget>>
    selectedWonders
  }
  class _EventsList {
    <<widget>>
    topHeight · blurOnScroll
  }
  class AppBackdrop { <<blur on scroll>> }
  class TimelineEventCard {
    <<widget>>
    year · text · darkMode
  }
  class HiddenCollectible { <<third collectible>> }
  class _TimelineBtn { <<widget>> }
  WonderEvents *-- AppHeader
  WonderEvents *-- _WonderImageWithTimeline
  _WonderImageWithTimeline *-- WonderTitleText
  _WonderImageWithTimeline *-- WondersTimelineBuilder : 3 tracks
  WonderEvents *-- _EventsList
  _EventsList *-- AppBackdrop : portrait
  _EventsList *-- TimelineEventCard : x6
  _EventsList *-- HiddenCollectible
  WonderEvents *-- _TimelineBtn
```

- `◆──` contains
- `──▷` reads model
- `┄┄▷` builds

## Read the events and open the global timeline · sequence {#sequence}

Scrolling only changes blur and remembers the offset; the button hands over to the timeline route.

```mermaid
sequenceDiagram
  actor User
  participant Events as _WonderEventsState
  participant Wonders as WondersLogic
  participant List as _EventsListState
  participant Router as GoRouter
  Events->>Wonders: getData()
  Events->>List: build with initialScrollOffset
  List-->>User: 6 cards slide in 100 ms apart
  User->>List: scroll
  List->>Events: _handleScroll(), remember offset
  List->>List: _buildScrollingListWithBlur(), backdrop blur 0 to 1 over 300 px
  User->>List: reach the end, hidden collectible
  User->>Events: tap Open global timeline
  Events->>Router: go …/timeline?type=wonder
```

## Key files {#files}

- `lib/ui/screens/wonder_events/wonder_events.dart` · one or two columns
- `lib/ui/screens/wonder_events/widgets/_events_list.dart` · cards, blur on scroll
- `lib/ui/screens/wonder_events/widgets/_wonder_image_with_timeline.dart` · image, mini timeline, era
- `lib/ui/common/wonders_timeline_builder.dart` · wonders on 3 tracks
- `lib/ui/common/timeline_event_card.dart` · year + text card
