## ADDED Requirements

### Requirement: Company-level deposit product configuration
The system SHALL provide a `rental_deposit_product_id` (Many2one → `product.product`) field on `res.company` to designate the rental deposit product, filtered by `is_rental_deposit = True`.

#### Scenario: Admin configures deposit product in settings
- **WHEN** admin opens Rental Settings
- **THEN** the system SHALL display a "Rental Deposit Product" field under the Deposit section
- **AND** the field SHALL only allow selection of products where `is_rental_deposit = True`

#### Scenario: Deposit product is set on company
- **WHEN** `rental_deposit_product_id` is set on the company
- **THEN** the system SHALL use this product for all auto-created deposit lines in that company's rental orders

### Requirement: Error when deposit product not configured
The system SHALL raise a `UserError` when a user attempts to add a rental product to a sale order and no deposit product is configured on the company.

#### Scenario: No deposit product configured
- **WHEN** a user adds a rental product (`rent_ok = True`) to a sale order line
- **AND** `company.rental_deposit_product_id` is not set
- **THEN** the system SHALL raise a `UserError` with message directing admin to configure the deposit product in Rental Settings
- **AND** the rental product SHALL NOT be added to the order
