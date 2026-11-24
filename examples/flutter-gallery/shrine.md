---
title: Shrine Study
sub: A retail study with a sign-in screen, a backdrop category menu, an asymmetric product grid and a cart that expands from a corner.
card_title: Shrine
card: Shop with a backdrop menu and an expanding cart
screenshots:
- file: shots/shrine/01_login.jpg
  caption: Sign in
- file: shots/shrine/02_products.jpg
  caption: The asymmetric product grid
- file: shots/shrine/03_cart_tab.jpg
  caption: 'Three products added: thumbnails in the corner tab'
- file: shots/shrine/04_cart.jpg
  caption: The expanded cart with shipping and tax
---

## What it does {#what}

Shrine is its own `MaterialApp` that opens on `/shrine/login`: a logo, username and password fields with cut corners, **CANCEL** (leaves the study through the root navigator) and **NEXT** (pushes `/shrine`; no check is made). The home is a backdrop: the front layer is the product grid, the back layer the category menu — All, Accessories, Clothing, Home — and tapping the title or menu icon slides the front layer down over 450 ms. Picking a category calls `setCategory` and closes the menu. The 38 products are laid out in an asymmetric, alternating one-and-two-card column pattern on a phone and balanced columns on desktop. Tapping a product adds one to the cart. The cart starts as a small tab in the corner showing up to 3 thumbnails and a **+N** count for the rest; tapping it expands it over 500 ms into the full cart, with a scrim behind, while the backdrop hides. The cart sums each line, adds $7 shipping per item and 6 % tax on the subtotal; **CLEAR CART** empties it and collapses the sheet, and back closes the cart before it leaves the study. The cart's contents and both animation positions are saved with state restoration.

## Logic · class diagram {#classes}

The app state is a scoped model, restored as a whole; the two animation controllers are owned by the app state and shared through an InheritedWidget.

```mermaid
classDiagram
  direction LR
  class ShrineApp {
    <<app>>
    loginRoute · homeRoute
  }
  class _ShrineAppState {
    <<app state>>
    _controller · _expandingController
    mobileBackdrop()
    desktopBackdrop()
    _onWillPop()
  }
  class _RestorableAppStateModel {
    <<restorable>>
    toPrimitives()
  }
  class AppStateModel {
    <<model>>
    productsInCart · totalCartQuantity
    selectedCategory
    subtotalCost · shippingCost · tax · totalCost
    getProducts()
    addProductToCart()
    removeItemFromCart()
    clearCart()
    loadProducts()
    setCategory()
  }
  class ProductsRepository {
    <<repository>>
    loadProducts()
  }
  class Product {
    <<data>>
    id · name · price · category
    isFeatured
  }
  class Category {
    <<data>>
    name
  }
  class PageStatus {
    <<inherited>>
    menuController · cartController
  }
  ShrineApp --> _ShrineAppState : createState
  _ShrineAppState --> _RestorableAppStateModel : _model
  _RestorableAppStateModel --> AppStateModel : value
  AppStateModel ..> ProductsRepository : loadProducts()
  AppStateModel o-- Product : _availableProducts
  Product --> Category
  _ShrineAppState *-- PageStatus : shares both controllers
```

- `──▷` holds
- `◇──` list of
- `◆──` contains
- `┄┄▷` uses

## Screen · widget composition {#widgets}

Three layers on one screen — backdrop, scrim, expanding cart — all driven by the two controllers.

```mermaid
classDiagram
  direction TB
  class _ShrineAppState { <<app state>> }
  class _UsernameTextField { <<sign in>> }
  class _PasswordTextField { <<sign in>> }
  class _CancelAndNextButtons { <<sign in>> }
  class _BackdropTitle { <<animated>> }
  class CategoryMenuPage {
    <<back layer>>
    onCategoryTap
  }
  class ProductPage { <<front layer>> }
  class MobileAsymmetricView {
    <<widget>>
    products
  }
  class TwoProductCardColumn { <<widget>> }
  class OneProductCardColumn { <<widget>> }
  class MobileProductCard {
    <<widget>>
    product · imageAspectRatio
  }
  class Scrim { <<widget>> }
  class ExpandingBottomSheet {
    <<widget>>
    hideController · expandingController
  }
  class ProductThumbnailRow { <<widget>> }
  class ExtraProductsNumber { <<widget>> }
  class ShoppingCartPage { <<page>> }
  class ShoppingCartRow {
    <<widget>>
    product · quantity
  }
  class ShoppingCartSummary { <<widget>> }
  _ShrineAppState *-- _UsernameTextField : login route
  _ShrineAppState *-- _PasswordTextField : login route
  _ShrineAppState *-- _CancelAndNextButtons : login route
  _ShrineAppState *-- _BackdropTitle
  _ShrineAppState *-- CategoryMenuPage
  _ShrineAppState *-- ProductPage
  ProductPage *-- MobileAsymmetricView
  MobileAsymmetricView *-- TwoProductCardColumn
  MobileAsymmetricView *-- OneProductCardColumn
  TwoProductCardColumn *-- MobileProductCard
  OneProductCardColumn *-- MobileProductCard
  _ShrineAppState *-- Scrim
  _ShrineAppState *-- ExpandingBottomSheet
  ExpandingBottomSheet *-- ProductThumbnailRow : closed
  ExpandingBottomSheet *-- ExtraProductsNumber : closed
  ExpandingBottomSheet *-- ShoppingCartPage : open
  ShoppingCartPage *-- ShoppingCartRow
  ShoppingCartPage *-- ShoppingCartSummary
```

- `◆──` contains

## Add to the cart and check out · sequence {#sequence}

The grid, the corner tab and the cart all listen to the same model.

```mermaid
sequenceDiagram
  actor User
  participant Menu as CategoryMenuPage
  participant Model as AppStateModel
  participant Card as MobileProductCard
  participant Sheet as ExpandingBottomSheet
  participant Cart as ShoppingCartPage
  User->>Menu: open the menu, tap CLOTHING
  Menu->>Model: setCategory()
  Menu-->>User: front layer slides back up, clothing only
  User->>Card: tap a product
  Card->>Model: addProductToCart()
  Model-->>Sheet: thumbnail joins the row, +N after 3
  User->>Sheet: tap the cart tab
  Sheet->>Sheet: open(), expands over 500 ms
  Sheet->>Cart: shows the full cart
  Cart->>Model: totalCost
  User->>Cart: tap CLEAR CART
  Cart->>Model: clearCart()
  Cart->>Sheet: close()
```

## Key files {#files}

- `lib/studies/shrine/app.dart` · Shrine app, controllers, restoration
- `lib/studies/shrine/login.dart` · sign-in screen
- `lib/studies/shrine/backdrop.dart` · front and back layers
- `lib/studies/shrine/category_menu_page.dart` · category menu
- `lib/studies/shrine/expanding_bottom_sheet.dart` · corner cart that expands
- `lib/studies/shrine/shopping_cart.dart` · cart page and totals
- `lib/studies/shrine/model/` · app state, products, categories
- `lib/studies/shrine/supplemental/` · product grids and cards
