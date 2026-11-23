---
title: Settings Module
sub: Accounts, appearance, troubleshooting and About — one SwiftUI screen with a value-based navigation stack.
card_title: Settings
card: Accounts, appearance, OPML, about
---

## What it does {#what}

`SettingsView` is a single `List` split into sections — accounts, feeds (OPML import/export), appearance, troubleshooting, help, about — each row either an action (opens System Settings, opens a help URL in `SafariView`) or a `navigationRow` that pushes a `SettingsDestination` case onto a value-based `NavigationStack`. Tapping an existing account or "Add Account" both resolve to the same `AccountInspectorView`/account-type screens used from the sidebar's "Get Info", so an account only has one settings UI no matter how you reach it. "Add Account" offers four types — on My iPhone (local), iCloud, a web service (Feedly, Feedbin, NewsBlur, Bazqux, etc. — each OAuth or credentials-based) and self-hosted (FreshRSS). OAuth sign-in runs through `OAuthAuthorizationHandler`, a delegate-based wrapper around the account type's own authorization operation. Timeline settings is the one screen that's still UIKit (`TimelineSettingsViewController`, a `UICollectionViewController`) bridged into the SwiftUI stack with a `UIViewControllerRepresentable`. Importing an OPML file replaces the chosen account's feeds and folders; exporting writes the account's current tree to a file the system share sheet hands off.

## Logic · class diagram {#classes}

Every destination row carries a `SettingsDestination` case; `destinationView(_:)` is the one place that maps a case to the screen that handles it.

```mermaid
classDiagram
  direction LR
  class SettingsView {
    <<page>>
    model · path
    destinationView()
  }
  class SettingsModel {
    <<view-model>>
    accounts · showCloudKitStats
  }
  class AddAccountView {
    <<page>>
    presentationAnchor
  }
  class OAuthAuthorizationHandler {
    <<service>>
  }
  class AccountInspectorView {
    <<page>>
    account · isModal
  }
  class TimelineSettingsRepresentable {
    <<bridge>>
  }
  class TimelineSettingsViewController { <<page>> }
  class AccountManager {
    <<service>>
    shared · existingAccount()
  }
  SettingsView --> SettingsModel : model
  SettingsView ..> AddAccountView : destinationView(.addAccount)
  AddAccountView ..> OAuthAuthorizationHandler : web/self-hosted sign-in
  SettingsView ..> AccountInspectorView : destinationView(.account), same view the sidebar uses
  SettingsView ..> TimelineSettingsRepresentable : destinationView(.timeline)
  TimelineSettingsRepresentable *-- TimelineSettingsViewController : wraps
  SettingsModel ..> AccountManager : accounts
  AccountInspectorView ..> AccountManager : existingAccount()
```

- `──▷` holds
- `┄┄▷` uses

## Screen · widget composition {#widgets}

```mermaid
classDiagram
  direction TB
  class SettingsView { <<page>> }
  class GeneralSettingsView { <<widget>> }
  class SidebarSettingsView { <<widget>> }
  class ArticlesSettingsView { <<widget>> }
  class ActivityLogView { <<widget>> }
  class ErrorLogView { <<widget>> }
  class AccountStatsView { <<widget>> }
  class AboutView { <<widget>> }
  SettingsView ..> GeneralSettingsView : builds
  SettingsView ..> SidebarSettingsView : builds
  SettingsView ..> ArticlesSettingsView : builds
  SettingsView ..> ActivityLogView : builds
  SettingsView ..> ErrorLogView : builds
  SettingsView ..> AccountStatsView : builds
  SettingsView ..> AboutView : builds
```

- `┄┄▷` builds

## Add an iCloud account · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Settings as SettingsView
  participant Add as AddAccountView
  participant AM as AccountManager
  User->>Settings: tap Add Account
  Settings->>Add: push .addAccount
  Add-->>User: four account types
  User->>Add: picks iCloud
  Add->>AM: createAccount(type: .cloudKit)
  AM-->>Add: account created, or an error alert
  Add->>Settings: popDestination(), animations disabled
  Settings-->>User: new account row in the Accounts section
```

## Key files {#files}

- `iOS/Settings/SettingsView.swift` · the settings list, `SettingsDestination` routing
- `iOS/Settings/AddAccountView.swift` · the four account types
- `iOS/Account/` · per-type setup screens (local, iCloud, credentials)
- `iOS/AccountStats/AccountStatsView.swift` · per-account article/feed counts
- `iOS/Settings/TimelineSettingsViewController.swift` · the one UIKit settings screen
- `iOS/Settings/ArticleThemesView.swift`, `ArticleThemeImporter.swift` · installed article themes
