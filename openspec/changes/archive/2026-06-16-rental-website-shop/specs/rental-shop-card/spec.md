## ADDED Requirements

### Requirement: Rental rate shown on shop listing card
For products where `rent_ok = True` and at least one pricing rule exists, the shop listing card SHALL display the cheapest daily rental rate beneath the product name, formatted as "฿{amount} / Day".

#### Scenario: Rental product with pricing rules shows daily rate
- **WHEN** a visitor views `/shop` and a product has `rent_ok = True` and one or more `product_pricing_ids`
- **THEN** the product card displays the cheapest computed price-per-day as "฿{X} / Day"

#### Scenario: Non-rental product shows no rental rate
- **WHEN** a visitor views `/shop` and a product has `rent_ok = False`
- **THEN** the product card displays no rental rate — only the standard sale price

#### Scenario: Rental product with no pricing rules shows no rental rate
- **WHEN** a visitor views `/shop` and a product has `rent_ok = True` but `product_pricing_ids` is empty
- **THEN** the product card displays no rental rate badge
