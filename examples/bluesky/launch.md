---
title: Launch Module
sub: Restoring the last session behind the splash, the provider tree and shell, and the signed-out splash with Create account and Sign in.
card_title: Launch
card: Session restore, shell and signed-out splash
---

## What it does {#what}

`App` first restores the persisted state (`initPersistedState`), resolves the region (`Geo.resolve`) and sets up a device id, and renders nothing until all three are done. `InnerApp` then reads the last active account and calls `resumeSession` for it; a failed resume is logged and the app carries on signed out. Until the session check and the landing check are done, `Splash` keeps the native splash (logo and wordmark) on screen. Below it sits a deep tree of providers — theme, query client, composer, messages, moderation options, the signed-out view, the selected feed, unread notifications and more — and at the bottom `Shell`. Signed in, `Shell` renders `ShellInner`: the tab navigator plus the composer, dialogs and lightbox that can open over any tab. Without a session, `LoggedOut` takes over with a state machine of five screens — the splash (`NativeSplashScreen`, with **Create account** and **Sign in**), sign in, create account, a starter pack landing and a group-chat join request. When a session expires later, a toast says so and the signed-out view returns.

## Logic · class diagram {#classes}

Two gates — persisted state, then session — before the shell decides between the app and the signed-out view.

```mermaid
classDiagram
  direction LR
  class App {
    <<root component>>
    isReady
  }
  class InnerApp {
    <<component>>
    isReady
    hasCheckedLanding
  }
  class Splash { <<component>> }
  class SessionApiContext {
    <<context>>
    resumeSession()
    login()
    createAccount()
    logoutCurrentAccount()
  }
  class SessionStateContext {
    <<context>>
    accounts · currentAccount · hasSession
  }
  class Shell { <<component>> }
  class ShellInner { <<component>> }
  class TabsNavigator { <<navigator>> }
  class LoggedOut {
    <<screen>>
    screenState
    onPressBack()
    onPressDismiss()
  }
  class ScreenState {
    <<enum>>
    S_LoginOrCreateAccount · S_Login · S_CreateAccount
    S_StarterPack · S_GroupChatJoinRequest
  }
  App *-- InnerApp
  InnerApp ..> SessionApiContext : resumeSession()
  InnerApp ..> SessionStateContext : currentAccount
  InnerApp *-- Splash
  Splash *-- Shell
  Shell *-- ShellInner : signed in
  ShellInner *-- TabsNavigator
  Shell ..> LoggedOut : no session
  LoggedOut --> ScreenState : screenState
```

- `◆──` contains
- `──▷` holds
- `┄┄▷` uses

## Screen · component composition {#widgets}

The signed-out splash: full-bleed art, the logo, and two buttons.

```mermaid
classDiagram
  direction TB
  class LoggedOut { <<screen>> }
  class NativeSplashScreen {
    <<screen>>
    onPressSignin
    onPressCreateAccount
  }
  class Logo { <<component>> }
  class Logotype { <<component>> }
  class Button { <<component>> }
  class Login { <<screen>> }
  class Signup { <<screen>> }
  LoggedOut *-- NativeSplashScreen : S_LoginOrCreateAccount
  NativeSplashScreen *-- Logo
  NativeSplashScreen *-- Logotype
  NativeSplashScreen *-- Button : Create account · Sign in
  LoggedOut *-- Login : S_Login
  LoggedOut *-- Signup : S_CreateAccount
```

- `◆──` contains

## Signed-out view · state machine {#states}

```mermaid
stateDiagram-v2
  [*] --> S_LoginOrCreateAccount
  S_LoginOrCreateAccount --> S_Login : Sign in
  S_LoginOrCreateAccount --> S_CreateAccount : Create account
  S_Login --> S_LoginOrCreateAccount : back
  S_CreateAccount --> S_LoginOrCreateAccount : back
  [*] --> S_StarterPack : opened from a starter pack link
  [*] --> S_GroupChatJoinRequest : opened from a chat invite
  S_Login --> [*] : signed in
  S_CreateAccount --> [*] : account created
```

## Cold start · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Root as App
  participant Inner as InnerApp
  participant Api as SessionApiContext
  participant Splash as Splash
  participant Shell as Shell
  User->>Root: opens the app
  Root->>Root: restores persisted state, region, device id
  Root->>Inner: renders once ready
  Inner->>Api: resumeSession(), last active account
  Api-->>Inner: session restored, or none
  Inner->>Splash: isReady
  Splash-->>User: native splash fades out
  Splash->>Shell: renders the shell
  Shell-->>User: Home tab, or the signed-out splash
```

## Key files {#files}

- `src/App.tsx` · startup, providers, session restore
- `src/Splash.tsx` · native splash until ready
- `src/view/shell/index.tsx` · shell, dialogs, composer over the tabs
- `src/Navigation.tsx` · tab navigator and every route
- `src/view/com/auth/LoggedOut.tsx` · signed-out screens
- `src/view/com/auth/NativeSplashScreen.tsx` · Create account / Sign in splash
- `src/state/session/` · accounts, session API, agents
