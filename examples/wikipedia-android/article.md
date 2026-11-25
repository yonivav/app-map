---
title: Article Module
sub: The article reader — PageActivity and PageFragment around a WebView of Page Content Service HTML, with a JavaScript bridge, a back stack per tab and a bottom action bar.
card_title: Article
card: WebView reader with tabs and a JavaScript bridge
screenshots:
- file: shots/article/01_article.jpg
  caption: The article in its WebView, with the bottom action bar
- file: shots/article/02_scrolled.jpg
  caption: 'Save: the article goes into a reading list'
- file: shots/article/03_year_in_review.jpg
  caption: A campaign modal can open over an article
---

## What it does {#what}

Every article opens in `PageActivity`, which hosts `PageFragment` and keeps browser-like tabs (the toolbar shows their count). `PageFragment.loadPage()` pushes the title onto the current tab's back stack and hands it to `PageFragmentLoadState`, which fetches the page summary from the REST API (and its categories), points the `WebView` at the page's mobile-HTML through `CommunicationBridge.resetHtml()`, and upserts a `HistoryEntry` into Room. The page's JavaScript (the Page Content Service) talks back through the bridge as named messages — `setup`, `final_setup`, `link`, `reference`, `image`, `media`, `pronunciation`, `footer_item` and more; a link to another article goes through `LinkHandler` into `handleInternalLink()`, which opens talk and category pages in their own screens, scrolls to an anchor on the same page, and otherwise loads the new title onto the back stack. Back walks that stack before leaving the activity. A bottom `PageActionTabLayout` holds the most used actions (save, language, find in article, theme, contents, share by default) and the overflow has the rest — watchlist, talk page, edit history, new tab, categories, edit, view on map. Time spent reading is measured with an active timer that pauses in the background and is stored for the history entry (it feeds the Activity tab's reading time).

## Logic · class diagram {#classes}

The fragment owns the bridge and the load state; the load state owns the network and history writes.

```mermaid
classDiagram
  direction LR
  class PageActivity {
    <<activity>>
    loadPage()
  }
  class PageFragment {
    <<page>>
    bridge · linkHandler
    loadPage()
    handleInternalLink()
    onBackPressed()
    addTimeSpentReading()
  }
  class PageFragmentLoadState {
    <<loader>>
    load()
    goBack() · goForward()
    pageLoad()
  }
  class PageViewModel {
    <<model>>
    page · title · curEntry
    readingListPage · isWatched
  }
  class CommunicationBridge {
    <<JavaScript bridge>>
    resetHtml()
    addListener()
    execute()
    evaluate()
  }
  class LinkHandler {
    <<handler>>
    onInternalLinkClicked()
    onPageLinkClicked()
  }
  class Tab {
    <<data>>
    backStack · backStackPosition
  }
  class HistoryEntry {
    <<entity>>
    title · source · timestamp
  }
  class PageActionItem {
    <<enum>>
    SAVE · LANGUAGE · FIND_IN_ARTICLE · THEME
    CONTENTS · SHARE · EDIT_ARTICLE · VIEW_ON_MAP
  }
  PageActivity *-- PageFragment
  PageFragment --> PageFragmentLoadState
  PageFragment --> PageViewModel : model
  PageFragment --> CommunicationBridge : bridge
  PageFragment --> LinkHandler : linkHandler
  CommunicationBridge ..> LinkHandler : link messages
  PageFragmentLoadState --> Tab : current tab
  PageFragmentLoadState ..> CommunicationBridge : resetHtml()
  PageFragmentLoadState ..> HistoryEntry : upsert into Room
  PageFragment ..> PageActionItem : bottom bar and overflow
```

- `──▷` holds
- `◆──` contains
- `┄┄▷` uses

## Screen · view composition {#widgets}

```mermaid
classDiagram
  direction TB
  class PageActivity { <<activity>> }
  class PageFragment { <<page>> }
  class ObservableWebView { <<web view>> }
  class PageActionTabLayout { <<bottom bar>> }
  class ToCHandler { <<contents drawer>> }
  class ReferenceDialog { <<bottom sheet>> }
  class LinkPreviewDialog { <<bottom sheet>> }
  PageActivity *-- PageFragment
  PageFragment *-- ObservableWebView
  PageActivity *-- PageActionTabLayout
  PageFragment *-- ToCHandler
  PageFragment *-- ReferenceDialog : tap a reference
  PageActivity *-- LinkPreviewDialog : long-press or preview a link
```

- `◆──` contains

## Open an article and follow a link · sequence {#sequence}

The summary comes over HTTP; the HTML is loaded by the WebView itself, and every tap comes back as a bridge message.

```mermaid
sequenceDiagram
  actor User
  participant Page as PageFragment
  participant Load as PageFragmentLoadState
  participant Bridge as CommunicationBridge
  participant Lnk as LinkHandler
  User->>Page: open an article
  Page->>Page: loadPage(), pushes it on the back stack
  Page->>Load: load()
  Load->>Load: pageLoad(), REST summary and categories
  Load->>Bridge: resetHtml()
  Load->>Load: upserts the HistoryEntry
  Bridge-->>Page: setup, final_setup
  User->>Bridge: tap a blue link
  Bridge-->>Lnk: link message
  Lnk->>Lnk: onInternalLinkClicked()
  Lnk->>Page: hands over the title
  Page->>Page: handleInternalLink(), loads the next article
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/page/PageActivity.kt` · article activity, tabs, toolbar
- `app/src/main/java/org/wikipedia/page/PageFragment.kt` · WebView, bridge listeners, links, timers
- `app/src/main/java/org/wikipedia/page/PageFragmentLoadState.kt` · loading and the back stack
- `app/src/main/java/org/wikipedia/bridge/` · JavaScript bridge and actions
- `app/src/main/java/org/wikipedia/page/action/` · bottom action bar items
- `app/src/main/java/org/wikipedia/page/tabs/` · article tabs
- `app/src/main/java/org/wikipedia/page/references/` · reference bottom sheets
