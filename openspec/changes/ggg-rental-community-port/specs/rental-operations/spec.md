## ADDED Requirements

### Requirement: Pickup wizard
The system SHALL provide a `rental.order.wizard` transient model with `status='pickup'` that loads rental lines eligible for pickup (is_rental, qty_delivered < product_uom_qty), pre-fills expected quantities, and allows the user to confirm actual pickup quantities.

#### Scenario: Open pickup wizard
- **WHEN** a user clicks "Pickup" on a confirmed rental order
- **THEN** a wizard dialog opens showing each rental product with `qty_reserved` (ordered qty), and `qty_delivered` pre-filled with the remaining quantity to pick up

#### Scenario: Validate pickup
- **WHEN** the user confirms pickup quantities and clicks "Validate"
- **THEN** `qty_delivered` is updated on each sale order line, a log message is posted to the SO chatter, and the order's `rental_status` transitions to `return`

#### Scenario: Over-delivery on pickup
- **WHEN** the confirmed `qty_delivered` exceeds `product_uom_qty`
- **THEN** `product_uom_qty` is automatically increased to match the delivered quantity

### Requirement: Return wizard
The system SHALL provide the same `rental.order.wizard` transient model with `status='return'` that loads rental lines eligible for return (is_rental, qty_returned < qty_delivered), pre-fills expected return quantities, and processes returns including late fee calculation.

#### Scenario: Open return wizard
- **WHEN** a user clicks "Return" on a picked-up rental order
- **THEN** a wizard dialog opens showing each rented product with `qty_delivered` (picked up qty) and `qty_returned` pre-filled with the remaining quantity to return

#### Scenario: Validate return
- **WHEN** the user confirms return quantities and clicks "Validate"
- **THEN** `qty_returned` is updated on each sale order line, a log message is posted to the SO chatter

#### Scenario: Return quantity constraint
- **WHEN** `qty_returned` exceeds `qty_delivered` on a wizard line
- **THEN** the system raises a validation error

#### Scenario: Partial return
- **WHEN** the user returns fewer items than delivered
- **THEN** only the specified quantity is recorded as returned, and the order's `rental_status` remains `return`

### Requirement: Late fee calculation
The system SHALL calculate late fees when a return is processed after the grace period. The fee formula is: `days × extra_daily + hours × extra_hourly`, where delay = `now - return_date - min_extra_hour` (grace period).

#### Scenario: On-time return (within grace period)
- **WHEN** a return is processed within `min_extra_hour` hours after `rental_return_date`
- **THEN** no late fee is generated

#### Scenario: Late return generates fee
- **WHEN** a return is processed 3 days and 5 hours after `rental_return_date` (beyond 2-hour grace period)
- **THEN** a delay fee is calculated as `3 × extra_daily + 3 × extra_hourly` (3 hours after subtracting grace)

### Requirement: Automatic delay service line
The system SHALL automatically create a new `sale.order.line` with a service product for late fees when `_generate_delay_line()` is called during a late return.

#### Scenario: Delay line creation
- **WHEN** a late fee is calculated and is greater than zero
- **THEN** a new SO line is created with the company's `extra_product` (service), price = fee × qty_returned, qty_delivered = 1, and a description including the expected and actual return times

#### Scenario: Default delay product
- **WHEN** `extra_product` is not configured on the company
- **THEN** the system creates a "Rental Delay Cost" service product automatically

### Requirement: Company delay configuration
The system SHALL add to `res.company`: `extra_hour` (float, per-hour late fee, default 0), `extra_day` (float, per-day late fee, default 0), `min_extra_hour` (integer, grace period in hours, default 2, minimum 1), and `extra_product` (many2one to product.product for delay charges).

#### Scenario: Configure delay settings
- **WHEN** an admin sets `extra_hour=5.00`, `extra_day=25.00`, `min_extra_hour=3`
- **THEN** late returns beyond 3 hours are charged at $25/day + $5/hour

#### Scenario: Grace period minimum
- **WHEN** `min_extra_hour` is set to 0
- **THEN** the system raises a validation error (minimum is 1)

### Requirement: Settings UI for delay costs
The system SHALL expose delay configuration in `res.config.settings`: `extra_hour` and `extra_day` (via `ir.default` for new products), `min_extra_hour` and `extra_product` (related to company).

#### Scenario: Settings saved
- **WHEN** an admin changes delay cost settings and saves
- **THEN** new products inherit the default `extra_hourly`/`extra_daily` values, and the company's grace period and delay product are updated
