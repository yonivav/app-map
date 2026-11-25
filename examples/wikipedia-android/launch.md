---
title: Launch Module
sub: The main activity with its five-tab bottom navigation, and the first-run onboarding and personalization that run on top of it once.
card_title: Launch
card: Tabs, onboarding and personalization
screenshots:
- file: shots/launch/01_intro.jpg
  caption: 'First launch: the onboarding intro'
- file: shots/launch/02_languages.jpg
  caption: Languages found on the device
- file: shots/launch/03_personalization.jpg
  caption: Personalization starts after onboarding
---

## What it does {#what}

`MainActivity` is the launcher activity. It hosts `MainFragment`, whose `ViewPager2` holds one fragment per `NavTab` — Home, Saved, Search (the reading history), Activity — and a fifth bottom-navigation item, **More**, that opens a bottom sheet instead of a page. Tapping Search again while it is selected opens the search screen. On a first launch (`Prefs.isInitialOnboardingEnabled`, and not opened to preview a shared reading list) the activity starts `InitialOnboardingActivity`: a Compose flow of three screens — intro, data & privacy, and languages (with **Add language**). Finishing it turns the flag off and starts `PersonalizationActivity`, which asks about curiosity, interests and which Home feed to see first. When onboarding returns, the main activity switches the Home tab to the chosen feed (For You for a personalized choice, otherwise Community) and its language. Badges on the tabs mark a new recommended reading list on Saved and the unseen Activity onboarding or Year in Review on Activity; a notification bell sits in the toolbar.

## Logic · class diagram {#classes}

One activity, one fragment of tabs; each tab's fragment is created by its enum value.

```mermaid
classDiagram
  direction LR
  class MainActivity {
    <<activity>>
    onboardingLauncher
    onTabChanged()
    onNewIntent()
  }
  class MainFragment {
    <<page>>
    currentFragment
    handleIntent()
    onFeedSelectPage()
    settingsClick()
  }
  class NavTab {
    <<enum>>
    HOME · READING_LISTS · SEARCH · EDITS · MORE
    newInstance()
  }
  class NavTabFragmentPagerAdapter { <<adapter>> }
  class MenuNavTabDialog { <<bottom sheet>> }
  class InitialOnboardingActivity {
    <<activity>>
    newIntent()
  }
  class OnboardingScreen {
    <<enum>>
    INTRO · DATA_PRIVACY · LANGUAGES
  }
  class PersonalizationActivity {
    <<activity>>
    newIntent()
  }
  class PersonalizationPage {
    <<enum>>
    CURIOSITY · INTERESTS · HOME_PREFERENCE
  }
  class Prefs {
    <<preferences>>
    isInitialOnboardingEnabled
    homePreferenceSelection
  }
  MainActivity *-- MainFragment
  MainFragment --> NavTabFragmentPagerAdapter
  NavTabFragmentPagerAdapter ..> NavTab : newInstance()
  MainFragment ..> MenuNavTabDialog : More
  MainActivity ..> InitialOnboardingActivity : first launch
  InitialOnboardingActivity --> OnboardingScreen
  InitialOnboardingActivity ..> PersonalizationActivity : on finish
  PersonalizationActivity --> PersonalizationPage
  MainActivity ..> Prefs : isInitialOnboardingEnabled
```

- `──▷` holds
- `◆──` contains
- `┄┄▷` uses · opens

## Screen · composition {#widgets}

```mermaid
classDiagram
  direction TB
  class InitialOnboardingActivity { <<activity>> }
  class AppOnboardingScreen { <<composable>> }
  class InitialOnboardingScreen { <<composable>> }
  class InitialOnboardingIntroContent { <<composable>> }
  class InitialOnboardingDataPrivacyContent { <<composable>> }
  class InitialOnboardingLanguagesScreen { <<composable>> }
  InitialOnboardingActivity *-- AppOnboardingScreen
  AppOnboardingScreen *-- InitialOnboardingScreen
  InitialOnboardingScreen *-- InitialOnboardingIntroContent
  InitialOnboardingScreen *-- InitialOnboardingDataPrivacyContent
  InitialOnboardingScreen *-- InitialOnboardingLanguagesScreen
```

- `◆──` contains

## First launch · sequence {#sequence}

Onboarding is a separate activity; the main screen only learns the outcome through the activity result.

```mermaid
sequenceDiagram
  actor User
  participant Main as MainActivity
  participant Prefs as Prefs
  participant Onboard as InitialOnboardingActivity
  participant Personal as PersonalizationActivity
  participant Home as HomeFragment
  Main->>Prefs: isInitialOnboardingEnabled
  Prefs-->>Main: true on a first launch
  Main->>Onboard: newIntent(), launched for a result
  User->>Onboard: goes through intro, privacy, languages
  Onboard->>Prefs: isInitialOnboardingEnabled = false
  Onboard->>Personal: newIntent()
  User->>Personal: interests and which feed first
  Personal-->>Main: back to the tabs
  Main->>Home: updateLanguage(), selectTab()
```

## Key files {#files}

- `app/src/main/java/org/wikipedia/main/` · main activity and the tabs fragment
- `app/src/main/java/org/wikipedia/navtab/` · tab enum, pager adapter, More sheet
- `app/src/main/java/org/wikipedia/onboarding/` · initial onboarding
- `app/src/main/java/org/wikipedia/feed/personalization/` · interests and feed preference
- `app/src/main/java/org/wikipedia/WikipediaApp.kt` · application, languages, tabs
