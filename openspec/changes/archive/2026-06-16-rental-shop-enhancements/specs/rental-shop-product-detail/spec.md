## MODIFIED Requirements

### Requirement: Deposit amount displayed
The detail page SHALL display the `deposit_price` if it is greater than zero, labeled "Deposit" with the formatted amount and a translatable sub-label that reads "Pay on pick-up day" in English or the equivalent in the visitor's active language (e.g., "ซำระ ณ วันรับ" in Thai).

#### Scenario: Deposit shown with correct translated sub-label
- **WHEN** a rental product has `deposit_price > 0` and the visitor's language is Thai
- **THEN** the deposit row shows "ซำระ ณ วันรับ" as the sub-label (not "ซ้อระ ณ วันรับ")

#### Scenario: Deposit sub-label shown in English for English visitors
- **WHEN** a rental product has `deposit_price > 0` and the visitor's language is English
- **THEN** the deposit row shows "Pay on pick-up day" as the sub-label

#### Scenario: Deposit row hidden when zero
- **WHEN** a rental product has `deposit_price = 0` or is unset
- **THEN** no deposit row is displayed

## ADDED Requirements

### Requirement: Checkout disabled on product detail page for rental products
The Add-to-Cart form and Buy-Now button on `/shop/{product}` SHALL be hidden for products where `rent_ok = True`. The product title and rental pricing block SHALL still be visible.

#### Scenario: Rental product detail has no checkout form
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = True`
- **THEN** no Add-to-Cart button or Buy-Now button is rendered

#### Scenario: Rental product title and pricing still visible
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = True`
- **THEN** the product name, images, and rental pricing block are still displayed

#### Scenario: Non-rental product detail unchanged
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = False`
- **THEN** the standard Add-to-Cart form renders normally
