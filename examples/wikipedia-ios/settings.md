---
title: Settings Module
sub: The SwiftUI settings screen reached from the profile menu — languages, search, feeds, notifications, reading preferences, storage, donations, privacy and account.
card_title: Settings
card: Languages, feeds, reading and account
screenshots:
- file: shots/settings/01_profile.jpg
  caption: The profile menu, with Settings
- file: shots/settings/02_settings.jpg
  caption: 'Settings: account row and the main section'
- file: shots/settings/03_more.jpg
  caption: Editing, privacy and about
---

## What it does {#what}

Settings opens from the profile menu behind the account button in each tab's navigation bar: `ProfileCoordinator` starts `SettingsCoordinator`, which reads the current values (primary language, reading theme, account state) asynchronously and builds `WMFSettingsViewModel`, shown by `WMFSettingsViewController`. The first section is the account row — **Log in** when logged out, your username (or temporary-account name) otherwise. The main section has **My languages** (showing the primary one), **Search**, the Home feed settings (For You and Community, or the classic Explore settings), **Year in Review** when it is offered, **Push notifications**, **Reading preferences** (showing the current theme), **Article storage and syncing**, and **Clear cached data**, which asks first. Then come editing preferences (the default editor), donations (donation reminders, clear donation history), privacy (privacy policy, terms of use, safety, opening in the browser) and finally rate the app, help and about. Each row's action is a closure the coordinator supplies, so the SwiftUI view never knows where a row leads; values that change (language, theme) are re-read when the screen appears.

## Logic · class diagram {#classes}

The coordinator owns every navigation decision; the view model is just sections of rows with closures.

```mermaid
classDiagram
  direction LR
  class ProfileCoordinator {
    <<coordinator>>
    showSettings()
  }
  class SettingsCoordinator {
    <<coordinator>>
    start()
    asyncStart()
    fetchDynamicValues()
  }
  class WMFSettingsViewModel {
    <<view-model>>
    sections
  }
  class SettingsSection {
    <<data>>
    header · footer · items
  }
  class SettingsItem {
    <<data>>
    image · title · subtitle
    accessory · action
  }
  class AccessoryType {
    <<enum>>
    none · chevron · icon
  }
  class WMFSettingsDataController {
    <<data controller>>
    defaultEditMode()
    shouldShowYiRSettingsItem()
  }
  class WMFAuthenticationManager {
    <<service>>
    authStateIsTemporary
  }
  ProfileCoordinator ..> SettingsCoordinator : start()
  SettingsCoordinator ..> WMFSettingsViewModel : builds
  WMFSettingsViewModel o-- SettingsSection : sections
  SettingsSection o-- SettingsItem : items
  SettingsItem --> AccessoryType : accessory
  WMFSettingsViewModel --> WMFSettingsDataController : dataController
  SettingsCoordinator ..> WMFAuthenticationManager : account row
```

- `──▷` holds
- `◇──` list of
- `┄┄▷` uses

## Screen · view composition {#widgets}

```mermaid
classDiagram
  direction TB
  class WMFSettingsViewController { <<page>> }
  class WMFSettingsView { <<SwiftUI>> }
  class WMFSettingsViewModel { <<view-model>> }
  WMFSettingsViewController *-- WMFSettingsView
  WMFSettingsView --> WMFSettingsViewModel
```

- `◆──` contains
- `──▷` reads model

## Open Settings, change the languages · sequence {#sequence}

Settings is built asynchronously, because some row values come from async data.

```mermaid
sequenceDiagram
  actor User
  participant Profile as ProfileCoordinator
  participant Coord as SettingsCoordinator
  participant Model as WMFSettingsViewModel
  participant Screen as WMFSettingsViewController
  User->>Profile: tap the account button, then Settings
  Profile->>Coord: start()
  Coord->>Coord: asyncStart()
  Coord->>Coord: fetchDynamicValues(), language and theme
  Coord->>Model: WMFSettingsViewModel(username, language, theme)
  Coord->>Screen: pushes the settings screen
  User->>Screen: tap My languages
  Screen->>Model: the row's action
  Model-->>Coord: opens the languages editor
```

## Key files {#files}

- `Wikipedia/Code/SettingsCoordinator.swift` · builds settings and handles every row
- `Wikipedia/Code/ProfileCoordinator.swift` · profile menu that opens settings
- `WMFComponents/Sources/WMFComponents/Components/Settings/` · settings view, view model and sub-screens
- `WMFData/Sources/WMFData/Data Controllers/Settings/` · stored settings
