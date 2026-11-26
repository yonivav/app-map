---
title: Composer Module
sub: Writing a post, a reply or a whole thread — text up to 300 characters per post, up to 4 images or a video, drafts, and publishing with a confirmed round-trip.
card_title: Composer
card: Posts, threads, media and drafts
---

## What it does {#what}

The composer opens over any screen: `useComposerControls().openComposer()` stores the options (a reply target, a quote, a mention, initial text or images) in the shell's composer state, and the shell's `Composer` renders `ComposePost` when that state is set. Everything you write is a thread: `composerReducer` holds a list of posts, each with its rich text, embeds and languages, and **Add post** appends another one. A post can carry up to 4 images or one video (uploaded and processed while you keep typing; with "publish on upload" it posts when processing finishes), a link card, a quote or a GIF. **Post** is enabled when at least one post has content, none is over 300 characters, and no media is still uploading. Publishing calls `post()` from the API library for the whole thread, then waits for the app view to see it — retrying up to 5 times — before closing, so the new post appears in your feeds and thread right away. Leaving with unsaved text offers to save a draft (up to 1,000 characters); drafts can be reopened later. Alt-text reminders, a language suggestion, interaction settings (who can reply, quote) and a thread gate are part of the same screen.

## Logic · class diagram {#classes}

```mermaid
classDiagram
  direction LR
  class useComposerControls {
    <<hook>>
  }
  class Composer { <<component>> }
  class ComposePost {
    <<screen>>
    replyTo · initQuote · initText · initImageUris
    onPressPublish()
  }
  class composerReducer {
    <<reducer>>
  }
  class ComposerAction { <<data>> }
  class useSaveDraftMutation { <<hook>> }
  class SessionStateContext { <<context>> }
  useComposerControls ..> Composer : opening sets the state it shows
  Composer *-- ComposePost
  ComposePost ..> composerReducer : dispatch ComposerAction
  composerReducer ..> ComposerAction
  ComposePost ..> useSaveDraftMutation : save a draft
  ComposePost ..> SessionStateContext : current account
```

- `◆──` contains
- `┄┄▷` uses

## Screen · component composition {#widgets}

```mermaid
classDiagram
  direction TB
  class ComposePost { <<screen>> }
  class ComposerTopBar { <<component>> }
  class ComposerReplyTo { <<component>> }
  class ComposerPost { <<component>> }
  class ComposerFooter { <<component>> }
  class ComposerPills { <<component>> }
  class AltTextReminder { <<component>> }
  class SuggestedLanguage { <<component>> }
  ComposePost *-- ComposerTopBar : Cancel, Post
  ComposePost *-- ComposerReplyTo
  ComposePost *-- ComposerPost : one per post in the thread
  ComposePost *-- ComposerPills : who can reply, labels
  ComposePost *-- ComposerFooter : media, GIF, emoji, language, count
  ComposePost *-- AltTextReminder
  ComposePost *-- SuggestedLanguage
```

- `◆──` contains

## Write and publish a thread · sequence {#sequence}

```mermaid
sequenceDiagram
  actor User
  participant Controls as useComposerControls
  participant Compose as ComposePost
  participant Reducer as composerReducer
  User->>Controls: new post button, opens the composer
  Controls-->>Compose: composer state set, it opens
  User->>Compose: types, adds 2 images
  Compose->>Reducer: update_post
  User->>Compose: Add post
  Compose->>Reducer: add_post
  User->>Compose: Post
  Compose->>Compose: onPressPublish(), canPost
  Compose->>Compose: posts the whole thread through the API library
  Note over Compose: waits for the app view to see it, up to 5 tries
  Compose-->>User: closes — the post shows in feeds
```

## Key files {#files}

- `src/view/com/composer/Composer.tsx` · composer screen and publishing
- `src/view/com/composer/state/composer.ts` · thread reducer, limits
- `src/view/com/composer/` · text input, photos, video, link cards, footer
- `src/state/shell/composer/` · open and close from anywhere
- `src/view/shell/Composer.tsx` · shows the composer over the shell
- `src/lib/api/index.ts` · `post()`: records, blobs, thread gate
