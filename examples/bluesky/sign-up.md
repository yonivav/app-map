---
title: Sign Up Module
sub: Creating an account in three steps — your details, a handle, and a verification captcha — driven by one reducer.
card_title: Sign up
card: Three-step account creation
---

## What it does {#what}

`Signup` holds the whole flow in one `useReducer` (`SignupState`): the server and its description, email, password, date of birth, invite code, handle, the active step and errors. There are three steps, `SignupStep.INFO`, `HANDLE` and `CAPTCHA`; **next** and **prev** move one step and set the slide direction. `StepInfo` asks for the hosting provider (Bluesky by default), email, password and birth date, and blocks anyone under 13 (`MIN_ACCESS_AGE`); `StepHandle` checks the handle's availability as you type (throttled) and lists the requirements, up to 18 characters on a Bluesky domain; `StepCaptcha` shows the server's captcha in a web view when the server requires phone verification. `useSubmitSignup` validates again before submitting — a missing email, password, handle, birth date or captcha code sends you back to that step with its error — then calls `createAccount()` on the session API. Errors from the server map back to a step too: a taken or invalid handle returns to the handle step.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class Signup { <<screen>> }
  class SignupState {
    <<data>>
    activeStep · serviceUrl · email · password
    dateOfBirth · handle · inviteCode
  }
  class SignupStep {
    <<enum>>
    INFO · HANDLE · CAPTCHA
  }
  class useSubmitSignup {
    <<hook>>
  }
  class SignupContext { <<context>> }
  class SessionApiContext {
    <<context>>
    createAccount()
  }
  class useHandleAvailabilityQuery { <<hook>> }
  class StepInfo { <<component>> }
  class StepHandle { <<component>> }
  class StepCaptcha { <<component>> }
  Signup --> SignupState : useReducer
  SignupState --> SignupStep : activeStep
  Signup --> SignupContext : provides state and dispatch
  StepInfo ..> SignupContext : state and dispatch
  StepHandle ..> useHandleAvailabilityQuery : as you type
  Signup ..> useSubmitSignup : submit
  useSubmitSignup ..> SessionApiContext : createAccount()
```

- `──▷` holds
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class Signup { <<screen>> }
  class StepInfo { <<component>> }
  class StepHandle { <<component>> }
  class StepCaptcha { <<component>> }
  class HostingProvider { <<component>> }
  class DateField { <<component>> }
  class PasswordField { <<component>> }
  class BackNextButtons { <<component>> }
  class AppLanguageDropdown { <<component>> }
  Signup *-- StepInfo : INFO
  Signup *-- StepHandle : HANDLE
  Signup *-- StepCaptcha : CAPTCHA
  Signup *-- AppLanguageDropdown
  StepInfo *-- HostingProvider
  StepInfo *-- PasswordField
  StepInfo *-- DateField
  StepInfo *-- BackNextButtons
  StepHandle *-- BackNextButtons
```

- `◆──` contains

## Steps · state machine {#states}

```mermaid
stateDiagram-v2
  [*] --> INFO
  INFO --> HANDLE : next, details valid and 13 or older
  HANDLE --> CAPTCHA : next, handle available
  HANDLE --> INFO : prev
  CAPTCHA --> HANDLE : prev
  CAPTCHA --> [*] : createAccount() succeeds
  CAPTCHA --> HANDLE : server says the handle is taken
```

## Create an account · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Info as StepInfo
  participant Handle as StepHandle
  participant Submit as useSubmitSignup
  participant Api as SessionApiContext
  User->>Info: email, password, birth date, Next
  Info->>Info: dispatch next
  User->>Handle: types a handle
  Handle->>Handle: availability check, throttled
  User->>Handle: Next
  Handle->>Submit: submit
  Note over Submit: a missing field sends you back to its step
  Submit->>Api: createAccount()
  Api-->>User: signed in, onboarding starts
```

## Key files {#files}

- `src/screens/Signup/index.tsx` · signup screen and steps
- `src/screens/Signup/state.ts` · reducer, steps, submit
- `src/screens/Signup/StepInfo/` · details step
- `src/screens/Signup/StepHandle/` · handle step
- `src/screens/Signup/StepCaptcha/` · captcha step
