---
title: Reply Study
sub: An email client study with six mailboxes, swipe to star or delete, an expanding mail view, search and compose.
card_title: Reply
card: Email client with motion between screens
screenshots:
- file: shots/reply/01_inbox.jpg
  caption: Inbox, with the animated bottom app bar and FAB
- file: shots/reply/02_starred.jpg
  caption: 'Swiped left: starred in place'
- file: shots/reply/03_mail.jpg
  caption: A mail opened with a container transform
- file: shots/reply/04_compose.jpg
  caption: Compose
---

## What it does {#what}

Reply is its own `MaterialApp` at `/reply`, sharing one `EmailStore` (a `ChangeNotifier` provided with Provider) between every screen. The store holds 15 built-in emails split into inbox, outbox and drafts, and derives six mailboxes from them — Inbox, Starred, Sent, Trash, Spam and Drafts — by filtering on starred and trashed ids; emails 7 and 8 start in the trash. On a phone the mailbox sits above an animated bottom app bar: tapping the Reply logo pulls up a bottom drawer to 40 % with the mailbox list and folders, and picking one sets `selectedMailboxPage`. Swiping a card right past 80 % moves it to the trash; swiping left past 40 % stars it in place (and on the Starred mailbox removes it). Tapping a card expands it into the full mail view with a container transform, and sets `selectedEmailId`, which turns the FAB into a reply button. The search icon swaps the mailbox for `SearchPage` with a fade-through, and the FAB opens `ComposePage` the same way. On desktop the same store drives a navigation rail with a folder list and keeps the open mail inside a nested navigator.

## Logic · class diagram {#classes}

One store is the single source of truth; every widget selects the part it needs and rebuilds on `notifyListeners`.

```mermaid
classDiagram
  direction LR
  class ReplyApp {
    <<app>>
    homeRoute · composeRoute
  }
  class EmailStore {
    <<store>>
    inboxEmails · starredEmails · trashEmails
    selectedMailboxPage · selectedEmailId
    onSearchPage · onMailView
    starEmail() · unstarEmail()
    deleteEmail()
  }
  class Email {
    <<data>>
    id · sender · subject · message
    containsPictures
  }
  class InboxEmail {
    <<data>>
    inboxType
  }
  class InboxType {
    <<enum>>
    normal · spam
  }
  class MailboxPageType {
    <<enum>>
    inbox · starred · sent · trash · spam · drafts
  }
  class AdaptiveNav { <<widget>> }
  class _MobileNav { <<widget>> }
  class _DesktopNav { <<widget>> }
  class _MailNavigator { <<nested navigator>> }
  ReplyApp --> EmailStore : provides
  EmailStore o-- Email : inbox · outbox · drafts
  Email <|-- InboxEmail
  InboxEmail --> InboxType
  EmailStore --> MailboxPageType : selectedMailboxPage
  ReplyApp *-- AdaptiveNav
  AdaptiveNav *-- _MobileNav : phone
  AdaptiveNav *-- _DesktopNav : desktop
  _MobileNav *-- _MailNavigator
  AdaptiveNav ..> EmailStore : selectedMailboxPage
```

- `──▷` holds
- `◇──` list of
- `◆──` contains
- `──▷|` extends
- `┄┄▷` uses

## Screen · widget composition {#widgets}

The phone layout keeps the app bar, drawer and FAB fixed and swaps only the body.

```mermaid
classDiagram
  direction TB
  class _MobileNav { <<widget>> }
  class MailboxBody { <<widget>> }
  class MailPreviewCard {
    <<widget>>
    id · email
    onStar · onDelete
  }
  class _MailPreview { <<widget>> }
  class _MailPreviewActionBar { <<widget>> }
  class ProfileAvatar {
    <<atom>>
    avatar
  }
  class MailViewPage {
    <<page>>
    id · email
  }
  class SearchPage { <<page>> }
  class ComposePage { <<page>> }
  class _AnimatedBottomAppBar { <<widget>> }
  class BottomDrawer { <<widget>> }
  class _BottomDrawerDestinations { <<widget>> }
  class _ReplyFab { <<widget>> }
  class Email { <<data>> }
  _MobileNav *-- MailboxBody
  MailboxBody *-- MailPreviewCard : one per email
  MailPreviewCard *-- _MailPreview : closed
  _MailPreview *-- _MailPreviewActionBar
  _MailPreviewActionBar *-- ProfileAvatar
  MailPreviewCard *-- MailViewPage : opened
  _MobileNav *-- SearchPage : onSearchPage
  _MobileNav *-- _AnimatedBottomAppBar
  _MobileNav *-- BottomDrawer
  BottomDrawer *-- _BottomDrawerDestinations
  _MobileNav *-- _ReplyFab
  _ReplyFab *-- ComposePage : opened
  MailPreviewCard --> Email
```

- `◆──` contains
- `──▷` reads model

## Star an email, then read it · sequence {#sequence}

Swipes and taps only write to the store; the lists rebuild themselves.

```mermaid
sequenceDiagram
  actor User
  participant Card as MailPreviewCard
  participant Store as EmailStore
  participant Body as MailboxBody
  participant View as MailViewPage
  participant Fab as _ReplyFab
  User->>Card: swipe left past 40 %
  Card->>Store: starEmail()
  Note over Card: confirmDismiss returns false, so the card stays
  Store-->>Body: notifyListeners, star icon appears
  User->>Card: tap the card
  Card->>Store: selectedEmailId = id
  Card->>View: container transform opens MailViewPage
  Store-->>Fab: onMailView, FAB becomes reply
  User->>View: tap the collapse button
  View->>Store: selectedEmailId = -1
  Store-->>Fab: FAB becomes compose again
```

## Key files {#files}

- `lib/studies/reply/app.dart` · Reply app, theme, store restoration
- `lib/studies/reply/adaptive_nav.dart` · phone and desktop navigation, drawer, FAB
- `lib/studies/reply/model/` · emails and the store
- `lib/studies/reply/mailbox_body.dart` · list of mail cards
- `lib/studies/reply/mail_card_preview.dart` · swipeable mail card
- `lib/studies/reply/mail_view_page.dart` · full email
- `lib/studies/reply/search_page.dart` · search history
- `lib/studies/reply/compose_page.dart` · new email
