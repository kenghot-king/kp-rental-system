## ADDED Requirements

### Requirement: Sync Deposits button on rental order
The system SHALL provide a [Sync Deposits] button above the order lines section on the rental order form view. The button SHALL only be visible on rental orders in draft or sent state.

#### Scenario: Button visible on rental order
- **WHEN** a user opens a rental order in draft or sent state
- **THEN** a [Sync Deposits] button SHALL be visible above the order lines

#### Scenario: Button hidden on non-rental order
- **WHEN** a user opens a regular sale order
- **THEN** the [Sync Deposits] button SHALL NOT be visible

#### Scenario: Button hidden on confirmed order
- **WHEN** a user opens a confirmed rental order (state = sale)
- **THEN** the [Sync Deposits] button SHALL NOT be visible

### Requirement: Sync creates missing deposit lines
The system SHALL create deposit lines for rental lines that do not yet have a linked deposit line when the user clicks [Sync Deposits].

#### Scenario: Rental line without deposit
- **WHEN** a rental order has a rental line (Power Bank, qty 3, list_price 5000) with no deposit child
- **AND** the user clicks [Sync Deposits]
- **THEN** the system SHALL create a deposit line with:
  - `product_id` = company's `rental_deposit_product_id`
  - `name` = `[Deposit] Power Bank`
  - `price_unit` = 5000 (product's `list_price`)
  - `product_uom_qty` = 3
  - `tax_ids` = same as the rental line
  - `deposit_parent_id` = the rental line
  - `sequence` = rental line sequence + 1

### Requirement: Sync updates drifted deposit lines
The system SHALL update existing deposit lines when their values no longer match the parent rental line.

#### Scenario: Quantity drifted
- **WHEN** a rental line has qty 5 but its deposit child has qty 3
- **AND** the user clicks [Sync Deposits]
- **THEN** the deposit line's qty SHALL be updated to 5

#### Scenario: Price drifted
- **WHEN** a rental product's `list_price` is 8000 but the deposit line has `price_unit` 5000
- **AND** the user clicks [Sync Deposits]
- **THEN** the deposit line's `price_unit` SHALL be updated to 8000

### Requirement: Sync removes orphaned deposit lines
The system SHALL remove deposit lines whose parent rental line no longer exists.

#### Scenario: Parent rental line deleted
- **WHEN** a deposit line's `deposit_parent_id` points to a rental line that was removed from the order
- **AND** the user clicks [Sync Deposits]
- **THEN** the orphaned deposit line SHALL be removed

### Requirement: Error when no deposit product configured
The system SHALL raise a `UserError` when the user clicks [Sync Deposits] and no `rental_deposit_product_id` is configured on the company.

#### Scenario: No deposit product
- **WHEN** `company.rental_deposit_product_id` is not set
- **AND** the user clicks [Sync Deposits]
- **THEN** the system SHALL raise a `UserError` directing the admin to configure the deposit product in Rental Settings
