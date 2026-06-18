## ADDED Requirements

### Requirement: Base daily rate displayed prominently
On the `/shop/{product}` detail page for a rental product, the system SHALL display the cheapest daily rate as the primary price in large format: "฿{X} / Day".

#### Scenario: Rental product detail shows base daily rate
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = True` and pricing rules
- **THEN** the page displays "฿{cheapest_per_day} / Day" as the prominent price

#### Scenario: Non-rental product detail unchanged
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = False`
- **THEN** the standard sale price block is shown with no rental modifications

### Requirement: All pricing tiers listed
The detail page SHALL list all `product_pricing_ids` for the product, each showing total price and period duration (e.g., "฿1,000 / 12 Days").

#### Scenario: All pricing tiers displayed
- **WHEN** a rental product has multiple pricing rules
- **THEN** each rule is shown as a row: "฿{price} / {duration} {unit}"

#### Scenario: Best-value tier highlighted
- **WHEN** multiple pricing tiers are displayed
- **THEN** the tier with the lowest computed price-per-day is visually highlighted (distinct background color and a per-day rate badge, e.g. "฿83/DAY")

### Requirement: Deposit amount displayed
The detail page SHALL display the `deposit_price` if it is greater than zero, labeled "Deposit" with the formatted amount and the sub-label "(ซ้อระ ณ วันรับ)".

#### Scenario: Deposit shown when set
- **WHEN** a rental product has `deposit_price > 0`
- **THEN** the detail page displays "Deposit ฿{deposit_price}" with sub-label "(ซ้อระ ณ วันรับ)"

#### Scenario: Deposit row hidden when zero
- **WHEN** a rental product has `deposit_price = 0` or is unset
- **THEN** no deposit row is displayed
