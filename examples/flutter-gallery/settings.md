---
title: Settings Module
sub: A panel that slides down from behind the home page and changes text size, direction, locale, platform, theme and speed for the whole app.
card_title: Settings
card: App-wide text, locale, platform and theme options
screenshots:
- file: shots/settings/01_panel.jpg
  caption: The settings panel slid down over the home page
- file: shots/settings/02_theme.jpg
  caption: Only one option is expanded at a time
- file: shots/settings/03_links.jpg
  caption: Slow motion, About and Feedback
---

## What it does {#what}

The settings icon in the top corner morphs into a close icon over 500 ms while `Backdrop` slides the settings page down from the top and pushes the home page down until only its 64 pt header shows; on a phone the panel takes 600 ms, and over its last 60 % the setting rows spread apart by 4 pt each. There are five expandable options and one switch: **Text scaling** (system, 0.8, 1.0, 2.0, 3.0), **Text direction** (locale-based, LTR, RTL — Arabic, Farsi, Hebrew, Pashto and Urdu count as RTL), **Language** (system first, then every supported locale sorted by its native name), **Platform mechanics** (Android, iOS, macOS, Linux, Windows), **Theme** (system, dark, light) and **Slow motion**, which sets `timeDilation` to 5 after a 150 ms delay so you see the UI start to react first. Only one option is expanded at a time, and closing the panel collapses it. Every choice builds a new `GalleryOptions` with `copyWith` and hands it to `ModelBinding`, which rebuilds the whole app, studies included. Escape closes the panel on desktop, where it is a 560 pt high floating card instead.

## Logic · class diagram {#classes}

The options are one immutable value; changing a setting replaces it, and the InheritedWidget above `MaterialApp` rebuilds everything below.

```mermaid
classDiagram
  direction LR
  class GalleryApp { <<app>> }
  class ModelBinding { <<widget>> }
  class _ModelBindingState {
    <<state>>
    currentModel · _timeDilationTimer
    updateModel()
    handleTimeDilation()
  }
  class GalleryOptions {
    <<data>>
    themeMode · customTextDirection
    locale · platform · timeDilation
    textScaleFactor()
    resolvedTextDirection()
    copyWith()
    of()
    update()
  }
  class _BackdropState {
    <<state>>
    _settingsPanelController · _iconController
    _isSettingsOpenNotifier
    _toggleSettings()
  }
  class _SettingsPageState {
    <<page state>>
    _expandedSettingId
    onTapSetting()
    _getLocaleOptions()
  }
  class _ExpandableSetting {
    <<enum>>
    textScale · textDirection · locale
    platform · theme
  }
  class CustomTextDirection {
    <<enum>>
    localeBased · ltr · rtl
  }
  GalleryApp *-- ModelBinding : initialModel
  ModelBinding --> _ModelBindingState : createState
  _ModelBindingState --> GalleryOptions : currentModel
  _BackdropState ..> _SettingsPageState : animationController
  _SettingsPageState --> _ExpandableSetting : _expandedSettingId
  _SettingsPageState ..> GalleryOptions : update()
  GalleryOptions --> CustomTextDirection : customTextDirection
```

- `──▷` holds
- `◆──` contains
- `┄┄▷` uses

## Screen · widget composition {#widgets}

Five generic option lists and one switch, each built from a map of value → label.

```mermaid
classDiagram
  direction TB
  class Backdrop { <<widget>> }
  class _SettingsIcon {
    <<animated>>
    toggleSettings
  }
  class SettingsIcon { <<painted icon>> }
  class SettingsPage { <<page>> }
  class _AnimateSettingsListItems {
    <<entrance>>
    animation
  }
  class SettingsListItem {
    <<widget>>
    title · selectedOption · optionsMap
    isExpanded
  }
  class DisplayOption {
    <<data>>
    title · subtitle
  }
  class ToggleSetting {
    <<widget>>
    text · value
  }
  class SettingsAbout { <<link>> }
  class SettingsFeedback { <<link>> }
  class SettingsAttribution { <<widget>> }
  class HomePage { <<page>> }
  Backdrop *-- SettingsPage : slides down
  Backdrop *-- HomePage : slides below
  Backdrop *-- _SettingsIcon
  _SettingsIcon *-- SettingsIcon
  SettingsPage *-- _AnimateSettingsListItems
  _AnimateSettingsListItems *-- SettingsListItem : 5
  _AnimateSettingsListItems *-- ToggleSetting : slow motion
  SettingsListItem --> DisplayOption : optionsMap
  SettingsPage *-- SettingsAbout
  SettingsPage *-- SettingsFeedback
  SettingsPage *-- SettingsAttribution
```

- `◆──` contains
- `──▷` reads model

## Switch to the dark theme · sequence {#sequence}

A setting never touches a widget: it swaps the model and lets the tree rebuild.

```mermaid
sequenceDiagram
  actor User
  participant Icon as _SettingsIcon
  participant Back as _BackdropState
  participant Page as _SettingsPageState
  participant Options as GalleryOptions
  participant Binding as _ModelBindingState
  User->>Icon: tap the settings icon
  Icon->>Back: _toggleSettings()
  Back->>Back: panel and icon controllers forward
  User->>Page: tap Theme
  Page->>Page: onTapSetting(), only Theme expanded
  User->>Page: pick Dark
  Page->>Options: copyWith(themeMode: dark)
  Page->>Options: update()
  Options->>Binding: updateModel()
  Binding->>Binding: handleTimeDilation(), unchanged
  Binding-->>User: MaterialApp rebuilds in the dark theme
```

## Key files {#files}

- `lib/pages/settings.dart` · settings page and links
- `lib/pages/settings_list_item.dart` · expandable option list, switch
- `lib/pages/backdrop.dart` · settings and home layers, icon
- `lib/pages/settings_icon/` · painted morphing icon
- `lib/data/gallery_options.dart` · options model and binding
