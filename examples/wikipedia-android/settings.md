---
title: Settings Module
sub: The More menu's bottom sheet and the Settings screen — preference XML loaded into an AndroidX PreferenceFragment, backed by Prefs.
card_title: Settings
card: More menu and preference screens
screenshots:
- file: shots/settings/01_more.jpg
  caption: The More bottom sheet
- file: shots/settings/02_settings.jpg
  caption: 'Settings: General preferences'
---

## What it does {#what}

The fifth bottom-navigation item, **More**, never selects a page: `MainFragment` shows `MenuNavTabDialog`, a bottom sheet with your account (or **Log in**), talk page, watchlist, contributions, the games hub, Places, donate and **Settings**, each forwarded to `MainFragment` through its `Callback`. Settings is `SettingsActivity` with `SettingsFragment`, a `PreferenceFragmentCompat` whose `SettingsPreferenceLoader` inflates `preferences.xml` and wires the rows: General (Wikipedia languages, customize the Home feed, Year in Review, link previews, collapse tables, app theme, default editor), recommended reading list, donations (reminders, delete local donation history), semantic search, and syncing (sync reading lists with your account, download reading-list articles); account and about sections follow. Rows that depend on remote configuration or your account state are hidden at load time — for example the whole syncing category when reading-list sync is disabled remotely. Values are stored through `Prefs`, a typed wrapper over shared preferences that the rest of the app reads directly, so a change takes effect the next time a screen reads it.

## Logic · class diagram {#classes}

Preferences are declared in XML; the loader only adds behaviour and visibility.

```mermaid
classDiagram
  direction LR
  class MainFragment {
    <<page>>
    settingsClick()
    loginClick()
    watchlistClick()
  }
  class MenuNavTabDialog { <<bottom sheet>> }
  class SettingsActivity {
    <<activity>>
    newIntent()
  }
  class SettingsFragment {
    <<page>>
    loadPreferences()
  }
  class SettingsPreferenceLoader {
    <<loader>>
    loadPreferences()
  }
  class BasePreferenceLoader {
    <<loader>>
    findPreference()
  }
  class Prefs {
    <<preferences>>
    isReadingListSyncEnabled
    homePreferenceSelection
  }
  class RemoteConfig {
    <<remote config>>
    config
  }
  MainFragment ..> MenuNavTabDialog : More
  MenuNavTabDialog ..> MainFragment : Callback
  MainFragment ..> SettingsActivity : settingsClick()
  SettingsActivity *-- SettingsFragment
  SettingsFragment ..> SettingsPreferenceLoader : loadPreferences()
  BasePreferenceLoader <|-- SettingsPreferenceLoader
  SettingsPreferenceLoader ..> RemoteConfig : hides disabled rows
  SettingsPreferenceLoader ..> Prefs : reads and writes
```

- `◆──` contains
- `──▷|` extends
- `┄┄▷` uses · opens

## Open Settings from More · sequence {#sequence}

The More item is intercepted before the pager ever moves.

```mermaid
sequenceDiagram
  actor User
  participant Main as MainFragment
  participant Menu as MenuNavTabDialog
  participant Settings as SettingsFragment
  participant Loader as SettingsPreferenceLoader
  User->>Main: tap More
  Main->>Menu: shows the bottom sheet, tab not selected
  User->>Menu: tap Settings
  Menu->>Main: settingsClick()
  Main->>Settings: starts SettingsActivity
  Settings->>Settings: loadPreferences()
  Settings->>Loader: loadPreferences(), preferences.xml
  Loader->>Loader: hides rows disabled by config or account
  Loader-->>User: General, reading lists, donations, syncing, about
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/navtab/MenuNavTabDialog.kt` · More bottom sheet
- `app/src/main/java/org/wikipedia/settings/SettingsActivity.kt` · settings activity
- `app/src/main/java/org/wikipedia/settings/SettingsFragment.kt` · preference fragment
- `app/src/main/java/org/wikipedia/settings/SettingsPreferenceLoader.kt` · rows and visibility
- `app/src/main/java/org/wikipedia/settings/Prefs.kt` · every stored preference
- `app/src/main/res/xml/preferences.xml` · settings layout
