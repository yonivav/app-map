# Design: React Native support

Status: draft, 2026-11-26. Nothing here is built yet.

## Goal

Point App Map at a React Native app (bare or Expo, TypeScript or JavaScript) and get the same map it
gives Flutter, iOS and Android apps: one page per area the user sees, diagrams where every box opens
its source, and a crop from the running app for each screen and component.

## What changes, what doesn't

| Part | Today | For React Native |
|---|---|---|
| Markdown pages, `build`, `verify`, `changes`, `sync`, `where`, popups, search | language-agnostic | **unchanged** |
| Indexer (`scripts/languages/`) | Dart, Swift, Kotlin, Java, Objective-C | **new** `typescript.py` for `.ts .tsx .js .jsx` (tree-sitter `tsx` and `typescript` grammars, already in `tree-sitter-language-pack`) |
| `facts` (role, builds, uses) | classes | **new roles** for components, hooks, stores, contexts; `builds` from JSX |
| Diagram conventions (`reference/diagrams.md`) | classes, widgets | **new section**: components and hooks as boxes (below) |
| Module discovery (SKILL.md step 1) | routes, tabs, folders | **new hints** for React Navigation and Expo Router |
| Screenshots | Flutter driver, XCUITest + lldb, Android instrumented test | **new adapter**: a dev-only JS helper that reports component rects; navigation through the existing iOS/Android drivers or Maestro |

## 1. Indexing TypeScript and JavaScript

React code is mostly functions, not classes, so the indexer has to decide which top-level
functions and constants are worth a box. One `typescript.py` module, the same output shape as the
others (`name, kind, file, from, to, supers, members`):

| Kind | Recognised by | Members |
|---|---|---|
| `component` | a function or `const X = (…) =>` whose name starts with a capital letter and that returns JSX; also `memo(…)`, `forwardRef(…)`, class components (`extends Component`) | its props (destructured parameters or the `Props` type's fields), the state it holds (`const [x, setX] = useState`), inner handlers (`const onPress = …`) |
| `hook` | `function useX` / `const useX =` | the values and functions it returns |
| `store` | Redux `createSlice({ name })`, Zustand `create(…)`, MobX classes, `createContext` + its Provider | slice reducers and selectors, store fields and actions, context value fields |
| `type` / `interface` / `enum` | TypeScript declarations | fields |
| `class`, `function`, `const` | everything else exported at top level | methods |

- `.tsx` and `.jsx` parse with the `tsx` grammar; `.ts` with `typescript`; plain `.js` with `tsx`
  too, since JSX in `.js` files is common in React Native.
- Generated and vendored code is skipped: `node_modules/`, `ios/Pods/`, `android/build/`,
  `*.d.ts`, `__generated__/`, `*.gen.ts`.
- Names collide more than in class-based code (every screen file may export `Header`), so a
  declaration also records whether it is exported, and lookups prefer the exported one in the
  same folder as the page's key files.

## 2. Facts

- **builds**: the components a component renders, read from its JSX (`<ProfileHeader … />`),
  excluding host components (`View`, `Text`, `Pressable`…) and library ones unless they are drawn
  on purpose.
- **uses**: the hooks it calls (`useProfile()`), stores and contexts it reads (`useSelector`,
  `useStore`, `useContext(X)`), and project functions it calls.
- **role** by kind first (above), then by name: `*Screen` → page, `use*` → hook, `*Store` /
  `*Slice` / `*Context` → store, `*Service` / `*Api` / `*Client` → service.

## 3. Diagrams

The page sections stay the same; what goes in the boxes changes.

- **Logic · class diagram** becomes "screen → hooks → stores and services". A screen box lists
  the state it holds and its handlers; a hook box lists what it returns; arrows are labelled with
  the hook or action called: `ProfileScreen ..> useProfile : useProfile()`,
  `useProfile ..> profileSlice : fetchProfile()`.
- **Screen · component composition**: the JSX tree, one box per project component, `*--` for
  "renders", with the props that matter as members.
- **State machine**: unchanged; for a real status union (`'idle' | 'loading' | 'error'`) or a
  reducer's states.
- **Sequence**: unchanged; participants are components, hooks, stores and services.
- New stereotypes: `<<screen>>`, `<<component>>`, `<<hook>>`, `<<store>>`, `<<context>>`.

## 4. Finding the modules

- **React Navigation**: navigators (`createNativeStackNavigator`, `createBottomTabNavigator`,
  `createDrawerNavigator`) and their `<Stack.Screen name component>` entries are the route table;
  each tab is a module, screens pushed from it belong to it.
- **Expo Router**: the `app/` folder is the route table; `(tabs)/` groups give the tabs, folders
  give the stacks.
- The Screens flowchart on the overview is drawn from the navigators or the `app/` tree.

## 5. Screenshots

The other adapters each read the running UI from the inside (Flutter's widget tree, lldb on
UIKit, Compose's inspector). For React Native the equivalent is React's own component tree in a
**debug build**:

1. **A dev-only helper**, `appMapShots.ts`, copied into the app like the Flutter helper (listed in
   `.git/info/exclude`, never committed) and imported once at the top of the entry file, guarded by
   `__DEV__`. On request it walks the React fiber tree from the root, and for every component whose
   name is in the map takes its first host view and calls `measureInWindow` on it. It prints the
   same `SHOT RECT <shot> <Component> <x> <y> <w> <h> <visible>` lines the other adapters print.
2. **Triggering a snap**: the native driver takes the screenshot, then asks the helper for the
   rects. Two options to try:
   - a deep link (`<scheme>://app-map/snap?id=…`) the helper listens to with `Linking`;
   - or a dev-menu-free channel: the helper polls a file in the app's documents folder that the
     driver writes (works on both simulators and emulators).
   The helper's output reaches the host through the console (`xcrun simctl spawn … log stream` on
   iOS, `adb logcat` on Android), which the existing adapters already read.
3. **Navigation** reuses what exists: the iOS adapter's XCUITest driver (by bundle id, taps by
   label or `testID`) and the Android adapter's UiAutomator-based test. A React Native app needs no
   changes for these, because `testID` and `accessibilityLabel` show up to both.
4. `app-map shots react-native ios|android …` picks the platform; `crop` works unchanged on the
   `SHOT RECT` lines.

Open question: whether the Hermes debug build keeps component names (`function.name`). It does
for development builds; release builds minify them, so screenshots require a debug build, as for
the other platforms.

## 6. First example app

[Bluesky's app](https://github.com/bluesky-social/social-app) (MIT, ~18k stars, Expo + React
Navigation, TypeScript) as the flagship live example, after checking its LICENSE and building it.
A smaller app first to develop against: an app generated from
[Ignite](https://github.com/infinitered/ignite)'s demo (check its license: GitHub reports it as
non-standard).

## 7. Plan

| Step | What | Done when |
|---|---|---|
| 1 | `typescript.py`: components, hooks, stores, types; tests with fixtures in `tests/` | the Ignite demo's components and hooks all resolve in `facts` |
| 2 | Facts: `builds` from JSX, `uses` from hooks/stores; new roles | `facts --dir` on a screen folder reads like the Flutter output |
| 3 | `reference/diagrams.md` and SKILL.md: React section, stereotypes, module hints | a fresh agent run on the Ignite demo produces a map that passes `verify` |
| 4 | Screenshot helper + `shots react-native` on the iOS simulator | crops for every screen of the Ignite demo |
| 5 | Same on Android | same crops on the emulator |
| 6 | Bluesky live example, README row, site card, CI entry | live link works, CI builds and verifies it |
| 7 | Release v0.6.0 and the Homebrew formula bump | `brew upgrade` gets it |

Steps 1–3 give a useful map without screenshots and could ship on their own as v0.6.0, with
screenshots following in v0.7.0.

## Risks

- **Name collisions** across files (many `Header`s): handled by the exported/nearby-folder rule
  in §1; may need the map to name a component by path in rare cases.
- **Dynamic composition** (components passed as props, render props, `screenOptions` headers):
  the indexer only sees static JSX; the agent reads the code for the rest, as SKILL.md already
  asks for UI built from data.
- **Expo vs bare**: Expo Go can't load a native test driver; screenshots need a development build
  (`npx expo run:ios` / `run:android`), which is the normal Expo workflow anyway.
