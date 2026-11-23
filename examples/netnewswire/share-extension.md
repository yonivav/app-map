---
title: Share Extension Module
sub: Adding a feed from Safari or another app's share sheet — a separate process that hands off to the main app.
card_title: Share Extension
card: Add a feed from the iOS share sheet
---

## What it does {#what}

The share extension is its own process (`NSExtensionPrincipalClass` in its `Info.plist`), so it can't call into `AccountManager` directly — it only shares an App Group container with the main app. `ShareViewController` is a bare `UINavigationController` hosting one screen, `ShareAddFeedViewController`, a grouped table with three sections: the feed's name (editable), a folder picker across every account's containers, and the URL being added. `resolveURL()` finds the shared link by trying, in order, Safari's JavaScript preprocessing result, a plain URL attachment, then plain text that parses as a URL — whichever the host app actually handed it. Tapping "Add Feed" doesn't add anything itself: it writes an `ExtensionFeedAddRequest` (name, URL, destination container ID) to a shared file via `ExtensionFeedAddRequestFile.save()` and completes the extension. The main app's `AppDelegate` starts `ExtensionFeedAddRequestFile.shared` watching that same file on launch and resume, and is what actually creates the feed — the same hand-off a Siri "Add Feed" shortcut (`AddFeedAppIntent`) uses to reach the main app without it being in the foreground.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class ShareViewController { <<extension root>> }
  class ShareAddFeedViewController {
    <<page>>
    url · selectedContainer
    resolveURL() · addFeed()
  }
  class ShareFolderPickerController {
    <<page>>
  }
  class ExtensionFeedAddRequest {
    <<data>>
    name · feedURL · destinationContainerID
  }
  class ExtensionFeedAddRequestFile {
    <<shared file>>
    save() · shared
  }
  class AppDelegate {
    <<app delegate>>
    start the watcher on launch
  }
  ShareViewController *-- ShareAddFeedViewController : root view controller
  ShareAddFeedViewController ..> ShareFolderPickerController : pick a folder
  ShareAddFeedViewController ..> ExtensionFeedAddRequest : addFeed(), builds the request
  ShareAddFeedViewController ..> ExtensionFeedAddRequestFile : save()
  AppDelegate ..> ExtensionFeedAddRequestFile : shared.start(), reads it back
```

- `◆──` contains
- `┄┄▷` uses

## Screen · widget composition {#widgets}

```mermaid
classDiagram
  direction TB
  class ShareAddFeedViewController { <<page>> }
  class ShareFolderPickerCell { <<widget>> }
  ShareAddFeedViewController *-- ShareFolderPickerCell : one row per folder
```

- `◆──` contains

## Add a feed from Safari's share sheet · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Safari
  participant Share as ShareAddFeedViewController
  participant File as ExtensionFeedAddRequestFile
  participant App as AppDelegate
  User->>Safari: Share → NetNewsWire
  Safari->>Share: launches with the page's URL
  Share->>Share: resolveURL() reads the JS preprocessing result
  Share-->>User: name field, folder picker, URL shown
  User->>Share: picks a folder, taps Add Feed
  Share->>File: save(ExtensionFeedAddRequest)
  Share->>Safari: extensionContext.completeRequest(), sheet dismisses
  Note over App: next time the main app launches or resumes
  App->>File: shared.start() picks up the saved request
  App->>App: creates the feed in the chosen folder
```

## Key files {#files}

- `iOS/ShareExtension/ShareViewController.swift` · the extension root and its one screen
- `iOS/ShareExtension/ShareFolderPickerController.swift` · the folder picker
- `iOS/ShareExtension/ShareFolderPickerCell.swift` · one folder row
