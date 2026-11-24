---
title: Launch Module
sub: The splash while the database migrates, the seven-step first-run onboarding, and the five-tab shell every other screen lives in.
card_title: Launch
card: Splash, migration, onboarding and the tab bar
screenshots:
- file: shots/launch/01_intro.jpg
  caption: 'First launch: the onboarding intro'
- file: shots/launch/02_languages.jpg
  caption: Languages found on the device, with an editor
- file: shots/launch/03_interests.jpg
  caption: 'Interests: topics and articles to follow'
- file: shots/launch/04_feed_preference.jpg
  caption: Which Home feed to see first
---

## What it does {#what}

`SceneDelegate` creates the window and calls `launchApp(in:waitToResumeApp:)` on the single `WMFAppViewController`. It covers itself with `SplashScreenViewController` (the launch-screen wordmark), then waits for `MWKDataStore` to finish its Core Data setup and library updates; if a migration is needed and takes longer than 4 s, the splash cross-fades over 0.3 s into a loading animation. When the data is ready, `setupControllers()` starts the background workers and `resumeApp` decides what to show. On the very first launch (no `WMFDidShowOnboarding` flag, and not opened from a link that skips it) `AppOnboardingCoordinator` presents a SwiftUI flow of seven steps: intro, data & privacy, languages (the device's languages, with an editor), a personalization intro, interests, feed preference (which Home segment to see first), and a loading step that builds the Home feed — it waits for the feed for at most 8 s and shows the animation for at least one 1 s loop. The last three steps show page dots and **Skip**, which keeps the default feed preference. Whatever path it takes, the app then builds five tabs — Home, Places, Saved, Activity, Search — each in its own navigation controller, and reopens on Home if it was in the background for 24 hours or more (unless the reader chose to open on Search).

## Logic · class diagram {#classes}

The tab bar controller is also the app coordinator: it owns the data store, the splash, the onboarding and the tab roots.

```mermaid
classDiagram
  direction LR
  class SceneDelegate { <<scene>> }
  class WMFAppViewController {
    <<app shell>>
    dataStore
    launchApp()
    migrateIfNecessary()
    resumeApp()
    loadMainUI()
    configureTabController()
    presentOnboardingIfNeeded()
    shouldShowOnboarding()
    shouldShowHomeOnLaunch()
  }
  class WMFAppTabType {
    <<enum>>
    main · places · saved · recent · search
  }
  class SplashScreenViewController {
    <<page>>
    maximumNonInteractiveTimeInterval
    triggerMigratingAnimation()
  }
  class LoadingAnimationViewController { <<page>> }
  class MWKDataStore { <<Core Data store>> }
  class AppOnboardingCoordinator {
    <<coordinator>>
    start()
    finish()
  }
  class WMFAppOnboardingViewModel {
    <<view-model>>
    steps · currentStepIndex
    advance() · skip()
    completeAfterLoadingFeed()
  }
  class HomeCoordinator { <<coordinator>> }
  SceneDelegate ..> WMFAppViewController : launchApp()
  WMFAppViewController --> MWKDataStore : dataStore
  WMFAppViewController --> SplashScreenViewController : splashScreenViewController
  SplashScreenViewController ..> LoadingAnimationViewController : after 4 s of migration
  WMFAppViewController --> AppOnboardingCoordinator : appOnboardingCoordinator
  AppOnboardingCoordinator --> WMFAppOnboardingViewModel
  WMFAppViewController --> WMFAppTabType : selectedIndex
  WMFAppViewController --> HomeCoordinator : homeCoordinator
```

- `──▷` holds
- `┄┄▷` uses · opens

## Onboarding · state machine {#states}

`advance()` moves one step; `skip()` (shown on the personalization steps) and the end of loading both finish.

```mermaid
stateDiagram-v2
  [*] --> intro
  intro --> dataPrivacy : next
  dataPrivacy --> languages : next
  languages --> personalizationIntro : next
  personalizationIntro --> interests : next
  interests --> feedPreference : next, loads the feed choices
  feedPreference --> loading : next
  loading --> [*] : feed loaded, at most 8 s
  personalizationIntro --> [*] : Skip
  interests --> [*] : Skip
  feedPreference --> [*] : Skip
```

## First launch · sequence {#sequence}

The splash stays up until the store is ready; onboarding replaces it, and the tabs load behind it.

```mermaid
sequenceDiagram
  actor User
  participant Scene as SceneDelegate
  participant App as WMFAppViewController
  participant Splash as SplashScreenViewController
  participant Store as MWKDataStore
  participant Onboarding as AppOnboardingCoordinator
  participant Steps as WMFAppOnboardingViewModel
  Scene->>App: launchApp()
  App->>App: showSplashView()
  App->>Store: finish setup
  App->>Store: run library updates and migrations
  Store-->>App: done, setupControllers()
  App->>App: resumeApp()
  App->>Onboarding: start(), no onboarding flag yet
  Onboarding->>Steps: intro, privacy, languages
  User->>Steps: Next ×5
  Steps->>Steps: completeAfterLoadingFeed()
  Steps-->>Onboarding: onCompletion
  Onboarding->>Onboarding: finish(), saves which feed to see first
  Onboarding->>App: loadMainUI() while onboarding still covers it
  Onboarding-->>App: dismissed, sets the onboarding flag
```

## Key files {#files}

- `Wikipedia/Code/SceneDelegate.swift` · window, URLs, user activities
- `Wikipedia/Code/WMFAppViewController.swift` · tab bar, launch, resume, routing
- `Wikipedia/Code/SplashScreenViewController.swift` · splash and migration animation
- `Wikipedia/Code/AppOnboardingCoordinator.swift` · first-run onboarding
- `WMFComponents/Sources/WMFComponents/Components/App Onboarding/` · onboarding views and steps
- `Wikipedia/Code/MWKDataStore.m` · Core Data store setup and migration
