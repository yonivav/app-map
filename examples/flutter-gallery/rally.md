---
title: Rally Study
sub: A personal-finance study with a sign-in screen, five animated tabs, donut charts and category detail pages.
card_title: Rally
card: Finance dashboard with charts
screenshots:
- file: shots/rally/01_overview.jpg
  caption: 'Overview: the first alert and the three summary cards'
- file: shots/rally/02_accounts.jpg
  caption: 'Accounts: a donut chart over coloured rows'
- file: shots/rally/03_details.jpg
  caption: 'A category''s details: line chart and transactions'
- file: shots/rally/04_bills.jpg
  caption: Bills
---

## What it does {#what}

Rally is a dark-themed `MaterialApp` that opens on `/rally/login`: username and password fields, a **LOGIN** button and a fingerprint button, both of which simply push `/rally` (pages change with a scaled shared-axis transition). The home is a five-tab bar — Overview, Accounts, Bills, Budgets, Settings — where only the selected tab shows its title, growing in over 200 ms. Overview shows the first alert and three cards (accounts, bills, budgets) with their totals; Accounts, Bills and Budgets each show an animated donut chart of their items with a coloured bar per row. All numbers come from `DummyDataService`: four accounts (Checking $2,215.13, Home Savings $8,678.88, Car Savings $987.48, Vacation $253), four bills and four budgets. Tapping a row expands it with a 350 ms container transform into a detail page with a line chart and a list of transactions. In Settings every item signs you out back to the login screen. The selected tab survives state restoration; on desktop the tab bar turns vertical and swipes go up and down.

## Logic · class diagram {#classes}

The screens are stateless views over static lists; only the tab index is state.

```mermaid
classDiagram
  direction LR
  class RallyApp {
    <<app>>
    loginRoute · homeRoute
  }
  class _MainView {
    <<sign in>>
    usernameController · passwordController
    _login()
  }
  class _HomePageState {
    <<page state>>
    _tabController · tabIndex
    _buildTabs()
    _buildTabViews()
  }
  class DummyDataService {
    <<service>>
    getAccountDataList()
    getBillDataList()
    getBudgetDataList()
    getAlerts()
    getDetailedEventItems()
    getSettingsTitles()
  }
  class AccountData {
    <<data>>
    name · primaryAmount · accountNumber
  }
  class BillData {
    <<data>>
    name · primaryAmount · dueDate
  }
  class BudgetData {
    <<data>>
    name · primaryAmount · amountUsed
  }
  class AlertData {
    <<data>>
    message · iconData
  }
  class DetailedEventData {
    <<data>>
    title · date · amount
  }
  RallyApp ..> _MainView : initialRoute login
  _MainView ..> _HomePageState : pushes the home route
  _HomePageState ..> DummyDataService : tab views read it
  DummyDataService ..> AccountData : builds
  DummyDataService ..> BillData : builds
  DummyDataService ..> BudgetData : builds
  DummyDataService ..> AlertData : builds
  DummyDataService ..> DetailedEventData : builds
```

- `┄┄▷` uses · opens

## Screen · widget composition {#widgets}

Accounts, Bills and Budgets share one layout: a donut chart over a list of coloured rows.

```mermaid
classDiagram
  direction TB
  class _HomePageState { <<page state>> }
  class _RallyTabBar { <<widget>> }
  class _RallyTab {
    <<widget>>
    titleText · icon · isVertical
  }
  class OverviewView { <<tab>> }
  class _AlertsView { <<widget>> }
  class _FinancialView { <<widget>> }
  class AccountsView { <<tab>> }
  class BillsView { <<tab>> }
  class BudgetsView { <<tab>> }
  class SettingsView { <<tab>> }
  class TabWithSidebar { <<layout>> }
  class FinancialEntityView {
    <<widget>>
    heroLabel · heroAmount
    segments · financialEntityCards
  }
  class RallyPieChart {
    <<chart>>
    heroLabel · heroAmount · segments
  }
  class FinancialEntityCategoryView {
    <<row>>
    indicatorColor · title · amount
  }
  class VerticalFractionBar { <<atom>> }
  class FinancialEntityCategoryDetailsPage { <<page>> }
  class RallyLineChart { <<chart>> }
  _HomePageState *-- _RallyTabBar
  _RallyTabBar *-- _RallyTab : 5
  _HomePageState *-- OverviewView
  OverviewView *-- _AlertsView
  OverviewView *-- _FinancialView : 3
  _HomePageState *-- AccountsView
  _HomePageState *-- BillsView
  _HomePageState *-- BudgetsView
  _HomePageState *-- SettingsView
  AccountsView *-- TabWithSidebar
  TabWithSidebar *-- FinancialEntityView
  FinancialEntityView *-- RallyPieChart
  FinancialEntityView *-- FinancialEntityCategoryView
  FinancialEntityCategoryView *-- VerticalFractionBar
  FinancialEntityCategoryView *-- FinancialEntityCategoryDetailsPage : opened
  FinancialEntityCategoryDetailsPage *-- RallyLineChart
```

- `◆──` contains

## Sign in and open an account · sequence {#sequence}

Nothing is fetched: every view builds its numbers from the dummy service on each build.

```mermaid
sequenceDiagram
  actor User
  participant Login as _MainView
  participant Home as _HomePageState
  participant Accounts as AccountsView
  participant Data as DummyDataService
  participant Row as FinancialEntityCategoryView
  participant Detail as FinancialEntityCategoryDetailsPage
  User->>Login: tap LOGIN
  Login->>Login: _login()
  Login->>Home: restorablePushNamed /rally
  User->>Home: tap the Accounts tab
  Home->>Home: _tabController listener, tabIndex = 1
  Home->>Accounts: shows the tab view
  Accounts->>Data: getAccountDataList()
  Data-->>Accounts: four accounts, donut animates in
  User->>Row: tap Checking
  Row->>Detail: container transform, 350 ms
  Detail->>Data: getDetailedEventItems()
  Detail-->>User: line chart and transactions
```

## Key files {#files}

- `lib/studies/rally/app.dart` · Rally app, routes, dark theme
- `lib/studies/rally/login.dart` · sign-in screen
- `lib/studies/rally/home.dart` · five-tab home
- `lib/studies/rally/tabs/` · overview, accounts, bills, budgets, settings
- `lib/studies/rally/finance.dart` · rows, details page, model builders
- `lib/studies/rally/charts/` · donut, line chart, fraction bar
- `lib/studies/rally/data.dart` · dummy data service
