### Requirement: Checkout disabled on product detail page for rental products
The Add-to-Cart form and Buy-Now button on `/shop/{product}` SHALL be visible and functional for products where `rent_ok = True`. The CTA section SHALL NOT be hidden. Checkout restriction is enforced at the cart page instead.

#### Scenario: Rental product detail has Add-to-Cart button
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = True`
- **THEN** the Add-to-Cart button is rendered and allows adding to cart

#### Scenario: Rental product title and pricing still visible
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = True`
- **THEN** the product name, images, and rental pricing block are still displayed

#### Scenario: Non-rental product detail unchanged
- **WHEN** a visitor views `/shop/{product}` for a product with `rent_ok = False`
- **THEN** the standard Add-to-Cart form renders normally
