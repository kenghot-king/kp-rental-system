## ADDED Requirements

### Requirement: Deposit product flag
The system SHALL provide an `is_rental_deposit` boolean field on `product.template` that marks a product as a rental security deposit.

#### Scenario: Mark product as deposit
- **WHEN** user enables the "Is Rental Deposit" checkbox on a product form
- **THEN** the product is flagged as a rental deposit product
- **AND** any SO line using this product is treated as a deposit line

#### Scenario: Default value
- **WHEN** a new product is created
- **THEN** the `is_rental_deposit` field SHALL default to `False`

### Requirement: Deposit flag visible on product form
The system SHALL display the `is_rental_deposit` checkbox on the product form view.

#### Scenario: Field visibility
- **WHEN** user opens the product form in rental context
- **THEN** the "Is Rental Deposit" checkbox is visible and editable
