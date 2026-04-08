## ADDED Requirements

### Requirement: Auto-create deposit line when rental product is added
The system SHALL automatically create a deposit line when a rental product is added to a sale order.

#### Scenario: Rental product added to SO
- **WHEN** a user adds a product with `rent_ok = True` to a sale order line
- **AND** `company.rental_deposit_product_id` is set
- **THEN** the system SHALL create a new SO line with:
  - `product_id` = `company.rental_deposit_product_id`
  - `name` = `[Deposit] {rental product name}`
  - `price_unit` = rental product's `list_price`
  - `product_uom_qty` = same as the rental line's quantity
  - `deposit_parent_id` = the rental line
  - `tax_id` = same taxes as the rental line (`tax_id`)
  - `is_rental` = False

#### Scenario: Non-rental product added to SO
- **WHEN** a user adds a product with `rent_ok = False` to a sale order line
- **THEN** the system SHALL NOT create a deposit line

### Requirement: Deposit line quantity syncs with parent
The system SHALL keep the deposit line quantity synchronized with its parent rental line quantity.

#### Scenario: Parent quantity increased
- **WHEN** the user changes the rental line's `product_uom_qty` from 2 to 5
- **THEN** the linked deposit line's `product_uom_qty` SHALL update to 5

#### Scenario: Parent quantity decreased
- **WHEN** the user changes the rental line's `product_uom_qty` from 5 to 1
- **THEN** the linked deposit line's `product_uom_qty` SHALL update to 1

### Requirement: Deposit line auto-deleted with parent
The system SHALL automatically remove the deposit line when its parent rental line is deleted.

#### Scenario: Rental line removed from draft order
- **WHEN** the user deletes a rental line from a draft sale order
- **THEN** the linked deposit line SHALL be removed from the order

### Requirement: Deposit line is read-only in UI
The deposit line SHALL be read-only in the sale order form view to prevent manual edits.

#### Scenario: User attempts to edit deposit line
- **WHEN** a deposit line exists on a sale order (identified by `deposit_parent_id` being set)
- **THEN** the fields `product_id`, `product_uom_qty`, `price_unit`, and `name` SHALL be read-only in the UI

### Requirement: Deposit line links to parent via deposit_parent_id
The system SHALL maintain a `deposit_parent_id` (Many2one → `sale.order.line`) field on `sale.order.line` to link deposit lines to their parent rental lines.

#### Scenario: Deposit line has parent reference
- **WHEN** a deposit line is auto-created
- **THEN** `deposit_parent_id` SHALL reference the rental line that triggered its creation

#### Scenario: Cascade delete on parent removal
- **WHEN** the parent rental line is deleted
- **THEN** the deposit line SHALL be deleted via `ondelete='cascade'`
