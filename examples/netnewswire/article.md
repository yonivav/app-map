---
title: Article Module
sub: Reading an article as rendered HTML, swiping between articles, Reader-view extraction, and "find in article".
card_title: Article
card: The reading view, Reader view, find-in-article
screenshots:
- file: shots/article/01_article.jpg
  caption: An article, with the toolbar to star, mark unread and share
- file: shots/article/02_find.jpg
  caption: Find in Article, from the share sheet
---

## What it does {#what}

`ArticleViewController` hosts a `UIPageViewController` of `WebViewController`s, one per article, so swiping left/right between unread articles is a page transition rather than a reload. Each `WebViewController` renders the article through a `PreloadedWebView` — a `WKWebView` kept pre-warmed in a small pool (`WebViewProvider`) because a fresh `WKWebView` flashes white on its first load in dark mode; the pool is flushed and refilled whenever the app returns to the foreground, since a backgrounded web view can silently lose its content process. Tapping the Reader-view button calls `toggleArticleExtractor()`, which starts an `ArticleExtractor` fetching a simplified, ad-free version of the page; while it's `.processing` the button animates, and on success the extracted HTML replaces the normal rendering until toggled off. `ArticleSearchBar`'s "find in article" scope searches the loaded page's text directly (not the article list) via `FindInArticleActivity`. An article's favicon loads through a custom `WKURLSchemeHandler` (`ArticleIconSchemeHandler`) rather than a network request, since it's already cached locally.

## Logic · class diagram {#classes}

The page controller and the extractor are the two moving parts; everything else renders a `WKWebView` one way or another.

```mermaid
classDiagram
  direction LR
  class ArticleViewController {
    <<page>>
    pageViewController · article
    coordinator
    toggleArticleExtractor()
  }
  class WebViewController {
    <<page>>
    article · articleExtractor
    extractedArticle · articleExtractorButtonState
    toggleArticleExtractor() · articleExtractionDidComplete()
  }
  class WebViewProvider {
    <<pool>>
    dequeueWebView() · replenishQueueIfNeeded()
  }
  class PreloadedWebView { <<pre-warmed WKWebView>> }
  class ArticleExtractor {
    <<service>>
    state · articleLink
  }
  class ArticleIconSchemeHandler {
    <<scheme handler>>
  }
  class SceneCoordinator {
    <<coordinator>>
    currentArticle · selectNextUnread()
  }
  ArticleViewController --> SceneCoordinator : coordinator
  ArticleViewController *-- WebViewController : one per page, in a UIPageViewController
  WebViewController --> ArticleExtractor : articleExtractor
  WebViewController ..> WebViewProvider : dequeueWebView()
  WebViewProvider o-- PreloadedWebView : pooled, pre-warmed
  WebViewController --> ArticleIconSchemeHandler : articleIconSchemeHandler
  ArticleExtractor ..> WebViewController : articleExtractionDidComplete()
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · widget composition {#widgets}

```mermaid
classDiagram
  direction TB
  class ArticleViewController { <<page>> }
  class ArticleExtractorButton { <<animates with ArticleExtractorButtonState>> }
  class ArticleSearchBar { <<find in article>> }
  class WebViewController { <<page>> }
  ArticleViewController *-- ArticleExtractorButton : toolbar
  ArticleViewController *-- ArticleSearchBar : find in article
  ArticleViewController *-- WebViewController : current page
```

- `◆──` contains

## Turn on Reader view · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Btn as ArticleExtractorButton
  participant WebVC as WebViewController
  participant Extractor as ArticleExtractor
  User->>Btn: tap
  Btn->>WebVC: toggleArticleExtractor()
  WebVC->>Extractor: starts extracting the current article's link
  Note over Extractor: state becomes .processing — button animates
  Extractor-->>WebVC: articleExtractionDidComplete(extractedArticle)
  WebVC->>WebVC: loads the extracted HTML instead of the page
  WebVC-->>Btn: articleExtractorButtonState = .on
  User->>Btn: tap again
  Btn->>WebVC: toggleArticleExtractor()
  WebVC-->>User: back to the normal page, button state = .off
```

## Key files {#files}

- `iOS/Article/ArticleViewController.swift` · the page controller, toolbar, extractor button
- `iOS/Article/WebViewController.swift` · one article's `WKWebView` and extractor state
- `iOS/Article/WebViewProvider.swift` · the pre-warmed `WKWebView` pool
- `iOS/Article/PreloadedWebView.swift` · the pooled `WKWebView` subclass
- `iOS/Article/ArticleIconSchemeHandler.swift` · favicon loading via a custom URL scheme
- `Shared/Article Extractor/ArticleExtractor.swift` · the Reader-view fetch
- `iOS/Article/ArticleSearchBar.swift`, `FindInArticleActivity.swift` · find in article
