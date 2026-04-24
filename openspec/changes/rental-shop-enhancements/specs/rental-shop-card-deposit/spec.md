## ADDED Requirements

### Requirement: Deposit shown on shop listing card
The `/shop` product card for a rental product SHALL display the deposit amount below the daily rate, formatted as "Deposit: ฿{amount}", only when `deposit_price > 0`.

#### Scenario: Card shows deposit when set
- **WHEN** a visitor views `/shop` and a rental product has `deposit_price > 0`
- **THEN** the product card displays "Deposit: ฿{deposit_price}" below the daily rate line

#### Scenario: Card hides deposit when zero
- **WHEN** a visitor views `/shop` and a rental product has `deposit_price = 0`
- **THEN** no deposit line appears on the card

#### Scenario: Non-rental product unaffected
- **WHEN** a visitor views `/shop` and a product has `rent_ok = False`
- **THEN** no deposit line appears on the card

## ADDED Requirements

### Requirement: Checkout disabled on shop listing card for rental products
The Add-to-Cart button on the `/shop` product card SHALL be hidden for products where `rent_ok = True`.

#### Scenario: Rental product card has no cart button
- **WHEN** a visitor views `/shop` and a product has `rent_ok = True`
- **THEN** no Add-to-Cart button is rendered on that product's card

#### Scenario: Non-rental product card unchanged
- **WHEN** a visitor views `/shop` and a product has `rent_ok = False`
- **THEN** the Add-to-Cart button renders normally
