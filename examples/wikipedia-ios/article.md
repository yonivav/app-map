---
title: Article Module
sub: The article reader, a web view of Page Content Service HTML with a native toolbar, table of contents, reference popovers and links that push the next article.
card_title: Article
card: Web view reader with native toolbar
screenshots:
- file: shots/article/01_article.jpg
  caption: The article in its web view, with the native toolbar
- file: shots/article/02_scrolled.jpg
  caption: 'Saved: the add-to-reading-list hint appears'
- file: shots/article/03_contents.jpg
  caption: The table of contents
---

## What it does {#what}

`ArticleCoordinator` creates an `ArticleViewController` for a URL and pushes it on the current tab. The controller asks `ArticleFetcher` for a mobile-HTML request from the Page Content Service, loads it into a `WKWebView` through its own URL scheme handler (so cached and offline copies are served from disk), and in parallel updates the article summary in Core Data with `ArticleSummaryController` — following redirects and adding the article to the read history. The page's JavaScript talks back through `ArticleWebMessagingController`: when setup finishes it sends the table of contents, and every tap on a link, reference, image or edit pencil arrives as an `Action`. A link to another article pushes a new article (through `LinkCoordinator`); a link to an anchor in the same article scrolls there. The bottom toolbar saves or unsaves (a long press adds to a reading list), opens the reading-themes popover (text size, theme), the table of contents, the language picker, find in page and share, and its **More** menu has revision history, talk page, watch and edit. After 30 s on screen an article is marked as significantly viewed, which feeds Because You Read; the scroll position is saved for when you come back.

## Logic · class diagram {#classes}

The view controller is split across about twenty extensions; the core is load, message handling and the toolbar delegate.

```mermaid
classDiagram
  direction LR
  class ArticleCoordinator {
    <<coordinator>>
    start()
  }
  class ArticleViewController {
    <<page>>
    article · articleURL · state
    load()
    loadPage()
    loadSummary()
    addToHistory()
    handleLink()
    startSignificantlyViewedTimer()
    saveArticleScrollPosition()
  }
  class ViewState {
    <<enum>>
    initial · loading · reloading · loaded · error
  }
  class ArticleFetcher {
    <<fetcher>>
    mobileHTMLRequest()
  }
  class ArticleSummaryController {
    <<service>>
    updateOrCreateArticleSummaryForArticle()
  }
  class SchemeHandler {
    <<URL scheme>>
    scheme
  }
  class ArticleWebMessagingController { <<JavaScript bridge>> }
  class ArticleToolbarController {
    <<controller>>
    toggleSave()
    showTableOfContents()
    share()
  }
  class LinkCoordinator {
    <<coordinator>>
    start()
  }
  class WMFArticle {
    <<Core Data entity>>
    addToReadHistory()
  }
  class MWKSavedPageList { <<saved pages>> }
  ArticleCoordinator ..> ArticleViewController : creates and pushes
  ArticleViewController --> ViewState : state
  ArticleViewController ..> ArticleFetcher : mobileHTMLRequest()
  ArticleViewController --> SchemeHandler : schemeHandler
  ArticleViewController ..> ArticleSummaryController : updateOrCreateArticleSummaryForArticle()
  ArticleViewController --> ArticleWebMessagingController : messagingController
  ArticleViewController --> ArticleToolbarController : toolbarController
  ArticleViewController --> WMFArticle : article
  ArticleViewController ..> MWKSavedPageList : toggles the saved page
  ArticleViewController ..> LinkCoordinator : start()
```

- `──▷` holds
- `┄┄▷` uses

## Screen · view composition {#widgets}

A native shell around one web view: lead image and toolbar outside, the article inside.

```mermaid
classDiagram
  direction TB
  class ArticleViewController { <<page>> }
  class WMFWebView { <<web view>> }
  class ArticleToolbarController { <<toolbar>> }
  class TableOfContentsViewController {
    <<panel>>
    displayMode
  }
  class ReadingThemesControlsViewController { <<popover>> }
  class ReferenceViewController { <<popover>> }
  class WMFImageGalleryViewController { <<modal>> }
  class AddArticlesToReadingListViewController { <<modal>> }
  ArticleViewController *-- WMFWebView
  ArticleViewController *-- ArticleToolbarController
  ArticleViewController *-- TableOfContentsViewController : contents
  ArticleViewController *-- ReadingThemesControlsViewController : text and theme
  ArticleViewController *-- ReferenceViewController : tap a reference
  ArticleViewController *-- WMFImageGalleryViewController : tap an image
  ArticleViewController *-- AddArticlesToReadingListViewController : long-press save
```

- `◆──` contains

## Load states · state machine {#states}

`ViewState` guards against loading twice and drives the refresh overlay.

```mermaid
stateDiagram-v2
  [*] --> initial
  initial --> loading : loadIfNecessary()
  loading --> loaded : web view finishes and summary updates
  loading --> error : bad request or load failure
  loaded --> reloading : pull to refresh or after an edit
  reloading --> loaded : new revision shown
  error --> loading : retry
```

## Open an article and follow a link · sequence {#sequence}

HTML and the summary load side by side; the page's JavaScript reports back as typed actions.

```mermaid
sequenceDiagram
  actor User
  participant Coord as ArticleCoordinator
  participant Article as ArticleViewController
  participant Fetcher as ArticleFetcher
  participant Summary as ArticleSummaryController
  participant Bridge as ArticleWebMessagingController
  participant Lnk as LinkCoordinator
  User->>Coord: tap an article anywhere
  Coord->>Coord: start()
  Coord->>Article: pushes it
  Article->>Article: load()
  Article->>Fetcher: mobileHTMLRequest()
  Article->>Summary: updateOrCreateArticleSummaryForArticle()
  Summary-->>Article: article, follows a redirect, addToHistory()
  Bridge-->>Article: setup, table of contents
  Article->>Article: startSignificantlyViewedTimer(), 30 s
  User->>Bridge: tap a blue link
  Bridge-->>Article: didReceive(link)
  Article->>Article: handleLink()
  Article->>Lnk: start(), pushes the next article
```

## Key files {#files}

- `Wikipedia/Code/ArticleViewController.swift` · article loading, web view, scroll state
- `Wikipedia/Code/ArticleViewController+ArticleWebMessageHandling.swift` · taps from the page
- `Wikipedia/Code/ArticleViewController+ArticleToolbarHandling.swift` · toolbar actions
- `Wikipedia/Code/ArticleWebMessagingController.swift` · JavaScript bridge and actions
- `Wikipedia/Code/ArticleToolbarController.swift` · bottom toolbar and More menu
- `Wikipedia/Code/ArticleCoordinator.swift` · opens an article in a tab
- `Wikipedia/Code/TableOfContentsViewController.swift` · contents panel
- `Wikipedia/Code/SchemeHandler/` · cached and offline page loading
