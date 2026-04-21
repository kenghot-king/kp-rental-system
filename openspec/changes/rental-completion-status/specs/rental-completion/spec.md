## ADDED Requirements

### Requirement: Completion status field on rental order
The system SHALL provide a stored computed field `rental_completion` on `sale.order` with values `complete` or `incomplete`. The field SHALL only be computed for confirmed rental orders (`is_rental_order=True` and `state='sale'`). For non-rental or unconfirmed orders, the field SHALL be `False`.

#### Scenario: Order with all conditions met
- **WHEN** a rental order has all rental items returned (sum of `qty_returned` >= sum of `qty_delivered` across `is_rental` lines), all posted non-deposit invoices paid (`payment_state == 'paid'`), and all deposit invoices fully refunded (total credit note amount >= total deposit invoice amount)
- **THEN** `rental_completion` SHALL be `'complete'`

#### Scenario: Order with items not fully returned
- **WHEN** a rental order has `sum(qty_returned) < sum(qty_delivered)` across rental lines
- **THEN** `rental_completion` SHALL be `'incomplete'`

#### Scenario: Order with unpaid invoices
- **WHEN** a rental order has at least one posted `out_invoice` (excluding deposit invoices) with `payment_state != 'paid'`
- **THEN** `rental_completion` SHALL be `'incomplete'`

#### Scenario: Order with deposit not fully refunded
- **WHEN** a rental order has deposit invoices and the total refunded amount (from non-cancelled `reversal_move_ids`) is less than the total deposit invoice amount
- **THEN** `rental_completion` SHALL be `'incomplete'`

#### Scenario: Order with no deposit invoices
- **WHEN** a rental order has no deposit invoices (no posted `out_invoice` with `is_rental_deposit` product lines)
- **THEN** the deposit refund condition SHALL be considered satisfied (skipped)

#### Scenario: Non-rental or unconfirmed order
- **WHEN** an order has `is_rental_order=False` or `state != 'sale'`
- **THEN** `rental_completion` SHALL be `False`

### Requirement: Completion detail text
The system SHALL provide a computed char field `rental_completion_detail` on `sale.order` containing a human-readable breakdown of completion progress. This field SHALL be used as tooltip text.

#### Scenario: Incomplete order with all three axes
- **WHEN** a rental order has deposit invoices and `rental_completion == 'incomplete'`
- **THEN** `rental_completion_detail` SHALL contain three lines: "Returned: X/Y", "Paid: X/Y", "Deposit refunded: X/Y" where X and Y are the actual counts/amounts

#### Scenario: Incomplete order without deposits
- **WHEN** a rental order has no deposit invoices and `rental_completion == 'incomplete'`
- **THEN** `rental_completion_detail` SHALL contain two lines: "Returned: X/Y" and "Paid: X/Y", omitting the deposit line

#### Scenario: Complete order
- **WHEN** `rental_completion == 'complete'`
- **THEN** `rental_completion_detail` SHALL be empty or a simple confirmation (no breakdown needed)

### Requirement: Deposit invoice identification
The system SHALL identify a posted `out_invoice` as a deposit invoice when any of its `invoice_line_ids` has a product where `is_rental_deposit == True`.

#### Scenario: Invoice with deposit product line
- **WHEN** a posted `out_invoice` contains an invoice line whose `product_id.is_rental_deposit == True`
- **THEN** the invoice SHALL be classified as a deposit invoice

#### Scenario: Invoice without deposit product line
- **WHEN** a posted `out_invoice` has no invoice lines with `is_rental_deposit` products
- **THEN** the invoice SHALL be classified as a non-deposit (rental) invoice

### Requirement: Completion status displayed in views
The system SHALL display the `rental_completion` field as a badge in Kanban, List, and Form views of rental orders. The badge SHALL show a tooltip with `rental_completion_detail` on hover when the status is `incomplete`.

#### Scenario: Badge visibility on confirmed rental order
- **WHEN** viewing a confirmed rental order (`state='sale'`, `is_rental_order=True`) in Kanban, List, or Form view
- **THEN** the completion badge SHALL be visible with value "Complete" (green) or "Incomplete" (red/orange)

#### Scenario: Badge hidden on non-rental order
- **WHEN** viewing a non-rental order or an unconfirmed rental order
- **THEN** the completion badge SHALL NOT be displayed

#### Scenario: Hover tooltip on incomplete status
- **WHEN** user hovers over an "Incomplete" badge
- **THEN** a tooltip SHALL appear showing the completion detail breakdown

### Requirement: Searchable and filterable completion status
The system SHALL support searching and filtering rental orders by `rental_completion` status.

#### Scenario: Filter by incomplete orders
- **WHEN** user applies filter `rental_completion == 'incomplete'`
- **THEN** only confirmed rental orders with incomplete status SHALL be shown

#### Scenario: Filter by complete orders
- **WHEN** user applies filter `rental_completion == 'complete'`
- **THEN** only confirmed rental orders where all items returned, all invoices paid, and all deposits refunded SHALL be shown

### Requirement: Recompute on state changes
The system SHALL recompute `rental_completion` when any of its underlying data changes: item return quantities, invoice payment states, or deposit credit note creation.

#### Scenario: Recompute on item return
- **WHEN** `qty_returned` changes on a rental order line
- **THEN** the parent order's `rental_completion` SHALL be recomputed

#### Scenario: Recompute on invoice payment
- **WHEN** a posted invoice linked to a rental order changes `payment_state`
- **THEN** the related order's `rental_completion` SHALL be recomputed

#### Scenario: Recompute on deposit credit note creation
- **WHEN** a deposit credit note is created and posted via `_create_deposit_credit_note()`
- **THEN** the related order's `rental_completion` SHALL be recomputed
