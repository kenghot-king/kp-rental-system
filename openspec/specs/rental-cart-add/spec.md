### Requirement: Add-to-Cart available for rental products on detail page
The `/shop/{product}` detail page SHALL display the Add-to-Cart button for products where `rent_ok = True`, identical to the standard non-rental product behavior.

#### Scenario: Rental product shows Add-to-Cart button
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = True`
- **THEN** the Add-to-Cart button is rendered and clickable

#### Scenario: Non-rental product unaffected
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = False`
- **THEN** the Add-to-Cart button renders normally as before
