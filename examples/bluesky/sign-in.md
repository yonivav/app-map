---
title: Sign In Module
sub: Signing in to Bluesky or any AT Protocol server — account picker, hosting-provider detection, a guard against look-alike handles, and password reset.
card_title: Sign in
card: Sign in, choose an account, reset a password
---

## What it does {#what}

`Login` is one screen with five forms that slide in order: **choose account** (when accounts were used on this device before), **sign in**, **forgot password**, **set new password** and **password updated**. `LoginForm` takes a handle or email and a password, with an indicator of the hosting provider. On **Next** it trims and lower-cases the identifier, adds the provider's domain when you typed a bare name, then asks `useHostingProvider` which server the account lives on — waiting for an autodetection still in flight. A network error stops the sign-in rather than guessing where to send the password. If detection lands on a server that isn't Bluesky's, wasn't chosen by hand, and isn't an account already signed in on this device, a dialog asks you to confirm the server first, so a look-alike handle can't capture the password. Then `login()` on the session API signs in; a server that asks for a two-factor code shows the code field. The form stays in its processing state on success while the app switches to the signed-in shell.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class Login {
    <<screen>>
    currentForm
    gotoForm()
    onPressForgotPassword()
  }
  class Forms {
    <<enum>>
    Login · ChooseAccount · ForgotPassword
    SetNewPassword · PasswordUpdated
  }
  class LoginForm {
    <<component>>
    isProcessing
    onPressNext()
  }
  class ChooseAccountForm { <<component>> }
  class ForgotPasswordForm { <<component>> }
  class SessionApiContext {
    <<context>>
    login()
  }
  class SessionStateContext {
    <<context>>
    accounts
  }
  Login --> Forms : currentForm
  Login *-- ChooseAccountForm
  Login *-- LoginForm
  Login *-- ForgotPasswordForm
  LoginForm ..> SessionApiContext : login()
  LoginForm ..> SessionStateContext : accounts, to trust a known DID
  ChooseAccountForm ..> SessionApiContext : login()
```

- `◆──` contains
- `──▷` holds
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class LoginForm { <<component>> }
  class FormContainer { <<layout>> }
  class HostingProviderIndicator { <<component>> }
  class PasswordField { <<component>> }
  class ConfirmHostingProviderDialog { <<dialog>> }
  class HostingProviderDialog { <<dialog>> }
  LoginForm *-- FormContainer
  LoginForm *-- HostingProviderIndicator
  LoginForm *-- PasswordField
  LoginForm *-- HostingProviderDialog : pick a server
  LoginForm *-- ConfirmHostingProviderDialog : non-Bluesky server detected
```

- `◆──` contains

## Sign in · sequence {#sequence}

The password is only sent once the server is known — and confirmed when it isn't Bluesky's.

```mermaid
sequenceDiagram
  actor User
  participant Form as LoginForm
  participant Api as SessionApiContext
  participant Shell as Shell
  User->>Form: handle and password, Next
  Form->>Form: onPressNext(), normalise the identifier
  Form->>Form: resolve the hosting provider, wait if still detecting
  Note over Form: a network error stops here — the password is never sent
  Form-->>User: confirm dialog if the server isn't Bluesky's and the account is new here
  User->>Form: confirms
  Form->>Api: login()
  Api-->>Form: session, or a two-factor code request
  Api-->>Shell: currentAccount set
  Shell-->>User: the signed-in tabs
```

## Key files {#files}

- `src/screens/Login/index.tsx` · the five forms and their order
- `src/screens/Login/LoginForm.tsx` · sign-in form, provider check, confirmation
- `src/screens/Login/ChooseAccountForm.tsx` · accounts used on this device
- `src/screens/Login/ForgotPasswordForm.tsx` · reset email
- `src/state/session/` · `login()` and the agents
