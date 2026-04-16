## ADDED Requirements

### Requirement: Deposit price field on rental product
The system SHALL provide a `deposit_price` field (Float, company-dependent) on `product.template`. This field represents the security deposit amount charged per unit for the rental product, and MAY differ per company.

#### Scenario: Field exists on rental product template
- **WHEN** a user opens a rental product form (`rent_ok = True`)
- **THEN** a `Deposit Price` field is visible in the rental tab

#### Scenario: Company-dependent value
- **WHEN** two companies have different deposit price expectations for the same product
- **THEN** each company SHALL see and store its own `deposit_price` value independently

#### Scenario: Zero deposit price
- **WHEN** `deposit_price` is set to 0
- **THEN** the deposit line SHALL be created with `price_unit = 0` (no fallback to `list_price`)

### Requirement: Deposit line price sourced from rental product's deposit_price
When `action_sync_deposits()` creates or updates a deposit line, the system SHALL use the rental product's `deposit_price` as `price_unit`.

#### Scenario: Create deposit line with deposit price
- **WHEN** [Sync Deposits] is clicked and a rental line has no existing deposit line
- **THEN** a new deposit line is created with `price_unit = rental_product.deposit_price`

#### Scenario: Update drifted deposit price
- **WHEN** [Sync Deposits] is clicked and an existing deposit line's `price_unit != rental_product.deposit_price`
- **THEN** the deposit line's `price_unit` is updated to `rental_product.deposit_price`

### Requirement: Deposit line tax sourced from deposit product's taxes
When `action_sync_deposits()` creates or updates a deposit line, the system SHALL use the company's rental deposit product's (`rental_deposit_product_id`) `taxes_id` as the deposit line's `tax_ids`. Fiscal position mapping SHALL NOT be applied.

#### Scenario: Create deposit line with deposit product taxes
- **WHEN** [Sync Deposits] is clicked and a rental line has no existing deposit line
- **THEN** a new deposit line is created with `tax_ids = deposit_product.taxes_id`

#### Scenario: Update drifted deposit taxes
- **WHEN** [Sync Deposits] is clicked and an existing deposit line's `tax_ids != deposit_product.taxes_id`
- **THEN** the deposit line's `tax_ids` is updated to `deposit_product.taxes_id`

### Requirement: Deposit sync check does not validate price or tax
`_check_deposit_sync()` SHALL NOT flag a mismatch when the deposit line's price or tax differs from any other field. It SHALL only flag structural issues: missing deposit lines, orphaned deposit lines, and quantity mismatches.

#### Scenario: Price difference not flagged
- **WHEN** a deposit line's `price_unit` differs from `rental_product.deposit_price`
- **THEN** `_check_deposit_sync()` SHALL NOT include a price mismatch in its results

#### Scenario: Qty mismatch still flagged
- **WHEN** a deposit line's `product_uom_qty` differs from the rental line's `product_uom_qty`
- **THEN** `_check_deposit_sync()` SHALL include a qty mismatch description in its results
