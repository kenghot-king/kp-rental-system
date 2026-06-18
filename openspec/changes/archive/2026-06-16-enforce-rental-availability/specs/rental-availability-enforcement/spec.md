## ADDED Requirements

### Requirement: Order-level availability action method

The system SHALL provide an action method `action_check_rental_availability()` on `sale.order` that, for each rental line on the order, validates that the product's currently available quantity (`free_qty` scoped to the order's warehouse) is greater than or equal to the sum of `product_uom_qty` across all lines for the same product on that order.

The method SHALL skip lines whose product is of `type == 'service'`.

The method SHALL raise a `ValidationError` with the helpful message format defined below if any product's order-total exceeds availability. The method SHALL return `True` if all lines pass.

#### Scenario: Order with all lines within availability — passes

- **WHEN** an order has rental lines for Product X (qty 2) and Product Y (qty 1)
- **AND** `Product X.free_qty = 5` and `Product Y.free_qty = 3`
- **THEN** `action_check_rental_availability()` returns `True` without error

#### Scenario: Order with one overbooked product — raises

- **WHEN** an order has a rental line for Product X with qty 5
- **AND** `Product X.free_qty = 2`
- **THEN** `action_check_rental_availability()` raises `ValidationError`

#### Scenario: Multi-line same-product summed before check

- **WHEN** an order has two rental lines for Product X: qty 3 and qty 2
- **AND** `Product X.free_qty = 4`
- **THEN** `action_check_rental_availability()` raises (because 3 + 2 = 5 > 4)

#### Scenario: Service products skipped

- **WHEN** an order has a rental line for a service product with qty 100
- **THEN** the method does not raise on that line regardless of any availability number

### Requirement: Confirmation enforces availability

The system SHALL invoke `action_check_rental_availability()` at the start of `_action_confirm()` on rental sale orders, before calling super. If the action raises, the confirmation is aborted and the order remains in `draft` state.

#### Scenario: Confirming an overbooked order is blocked

- **WHEN** a user clicks "Confirm" on a rental order whose total qty for Product X is 5 and `Product X.free_qty` is 2
- **THEN** the order does NOT transition to `sale` state
- **AND** the user sees the helpful availability error message

#### Scenario: Confirming an in-stock order succeeds

- **WHEN** a user clicks "Confirm" on a rental order whose lines are all within availability
- **THEN** the order transitions to `sale` state normally

#### Scenario: Drafts and quotations save without check

- **WHEN** a user creates a draft rental order with Product X qty 5 (`free_qty = 2`) and clicks Save
- **THEN** the save succeeds (no constraint blocks draft state)
- **AND** the order remains saved with the overbooked qty until either edited or attempted to confirm

### Requirement: Live onchange warning on lines

The system SHALL display a non-blocking warning via Odoo's onchange `{'warning': ...}` mechanism whenever the user edits `product_id` or `product_uom_qty` on a rental order line such that that single line's qty exceeds the product's `free_qty`. The warning is per-line; it does not sum across the order (that is the confirm-time check's role).

The system SHALL NOT show the warning for service products or non-rental lines.

#### Scenario: User types qty exceeding line availability

- **WHEN** a user is editing a rental order line and sets `product_uom_qty = 5`
- **AND** `Product X.free_qty = 2`
- **THEN** the form displays a warning dialog naming Product X, the requested 5, and the available 2

#### Scenario: User reduces qty back into availability

- **WHEN** the same user reduces qty from `5` back to `2`
- **THEN** no warning is displayed

### Requirement: Helpful error message format

The `ValidationError` raised by `action_check_rental_availability()` and the onchange `{'warning': ...}` SHALL share a single message format that includes:

- The product display name
- The requested `product_uom_qty` (post-summing for the confirm-time check; per-line for onchange)
- The currently available quantity at the warehouse
- The warehouse display name
- A corrective action hint ("Reduce the quantity to N or add more stock to proceed.")

The message SHALL NOT contain raw technical identifiers (no internal IDs, no Python field names) — only customer-facing terms.

#### Scenario: Error message is human-readable

- **WHEN** the confirm-time check fails because Product "Power Bank 10Kw" has order-total qty 5 and free 2 at warehouse "WH"
- **THEN** the error message reads (substantively):
  > Cannot rent 5 × Power Bank 10Kw.
  > Requested: 5
  > Currently available in WH: 2
  > Reduce the quantity to 2 or add more stock to proceed.
- **AND** the message contains no internal field names or record IDs
