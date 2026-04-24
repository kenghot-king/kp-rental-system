### Requirement: Checkout blocked on cart page when rental items present
The `/shop/cart` page SHALL disable the "Proceed to Checkout" button and display an explanatory notice when any cart line contains a product with `rent_ok = True`.

#### Scenario: Cart with rental item blocks checkout
- **WHEN** a visitor views `/shop/cart` and at least one order line has `product_id.rent_ok = True`
- **THEN** the "Proceed to Checkout" button is replaced with a disabled button and a message explaining rental items require a separate booking process

#### Scenario: Cart with only non-rental items proceeds normally
- **WHEN** a visitor views `/shop/cart` and no order lines have `rent_ok = True`
- **THEN** the standard "Proceed to Checkout" button is rendered and functional

#### Scenario: Empty cart unaffected
- **WHEN** a visitor views `/shop/cart` with an empty cart
- **THEN** the page renders normally with no rental-related changes
