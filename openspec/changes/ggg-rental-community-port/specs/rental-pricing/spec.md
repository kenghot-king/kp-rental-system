## ADDED Requirements

### Requirement: Temporal recurrence model
The system SHALL provide a `sale.temporal.recurrence` model with fields: `name` (translated), `duration` (integer, default 1), `unit` (selection: hour/day/week/month/year), `overnight` (boolean), `pickup_time` (float 0-24), `return_time` (float 0-24), and computed `duration_display` (e.g., "1 Day", "2 Weeks").

#### Scenario: Create hourly recurrence
- **WHEN** a recurrence is created with `duration=1`, `unit='hour'`
- **THEN** `duration_display` equals "1 Hour"

#### Scenario: Overnight recurrence
- **WHEN** a recurrence has `overnight=True`
- **THEN** the displayed unit shows "Night" instead of "Hour", and `pickup_time`/`return_time` fields are editable

#### Scenario: Pickup/return time constraints
- **WHEN** `pickup_time` or `return_time` is set to a value outside 0-24
- **THEN** the system raises a validation error

#### Scenario: Duration constraint
- **WHEN** `duration` is set to a negative value
- **THEN** the system raises a validation error

### Requirement: Default recurrence seed data
The system SHALL create default recurrences on installation: Hourly, 3 Hours, Daily, Nightly (24h overnight with 15:00 check-in / 10:00 check-out), Weekly, 2 Weeks, Monthly, Quarterly, Yearly, 3 Years, 5 Years.

#### Scenario: Fresh install
- **WHEN** the `ggg_rental` module is installed on a clean database
- **THEN** all 11 default recurrences exist in `sale.temporal.recurrence`

### Requirement: Pricing rules model
The system SHALL provide a `product.pricing` model with fields: `recurrence_id` (required, many2one to `sale.temporal.recurrence`), `price` (monetary, required), `product_template_id` (required), `product_variant_ids` (many2many, empty = all variants), `pricelist_id` (many2one, empty = default pricing), and computed `currency_id`.

#### Scenario: Create pricing rule
- **WHEN** a pricing rule is created with `recurrence_id=Daily`, `price=50.00`, `product_template_id=Bike`
- **THEN** the rule applies to all variants of Bike at $50/day on the default pricelist

#### Scenario: Variant-specific pricing
- **WHEN** a pricing rule specifies `product_variant_ids=[Red Bike]`
- **THEN** the rule applies only to the Red Bike variant

### Requirement: Pricing uniqueness constraint
The system SHALL prevent duplicate pricing rules for the same combination of (product_template, product_variants, pricelist, recurrence).

#### Scenario: Duplicate pricing rejected
- **WHEN** a second pricing rule is created with identical (template, variants, pricelist, recurrence) as an existing rule
- **THEN** the system raises a validation error

### Requirement: Duration-to-price calculation
The system SHALL compute rental prices using PERIOD_RATIO conversion (`hour=1, day=24, week=168, month=744, year=8928`) with ceiling rounding. Formula: `total = base_price × ceil(duration_in_rule_hours / recurrence_duration_in_hours)`.

#### Scenario: Exact duration match
- **WHEN** a product has a Daily pricing at $50 and the rental is exactly 2 days (48 hours)
- **THEN** the total price is $50 × 2 = $100

#### Scenario: Partial period ceiling rounded
- **WHEN** a product has a Daily pricing at $50 and the rental is 36 hours (1.5 days)
- **THEN** the total price is $50 × ceil(36/24) = $50 × 2 = $100

#### Scenario: Cross-unit conversion
- **WHEN** a product has a Weekly pricing at $300 and the rental is 10 days
- **THEN** duration_hours = 240, rule_hours = 168, periods = ceil(240/168) = 2, total = $300 × 2 = $600

#### Scenario: Zero duration
- **WHEN** duration is 0 or negative
- **THEN** the base price is returned

### Requirement: Best pricing selection
The system SHALL select the pricing rule that produces the minimum total cost for a given rental duration, evaluating all applicable rules across different recurrence units.

#### Scenario: Best price across rules
- **WHEN** a product has Daily ($50/day) and Weekly ($300/week) pricing, and the rental is 4 days
- **THEN** Daily: $50 × 4 = $200, Weekly: $300 × 1 = $300 → Daily is selected ($200)

#### Scenario: Weekly cheaper for longer rental
- **WHEN** a product has Daily ($50/day) and Weekly ($300/week) pricing, and the rental is 8 days
- **THEN** Daily: $50 × 8 = $400, Weekly: $300 × 2 = $600 → Daily is selected ($400)

#### Scenario: Pricelist-specific rules take priority
- **WHEN** a product has default pricing at $50/day and pricelist "VIP" pricing at $40/day
- **THEN** for VIP pricelist customers, the $40/day rule is used for best-price calculation

### Requirement: Duration computation
The system SHALL provide `_compute_duration_vals(start_date, end_date)` returning ceiling-rounded durations in all units: `{hour, day, week, month, year}`.

#### Scenario: Duration calculation
- **WHEN** start_date = 2024-10-01 10:00 and end_date = 2024-10-03 16:00
- **THEN** result includes `hour=54, day=3, week=1, month=1`

### Requirement: Pricelist rental price integration
The system SHALL override `product.pricelist._compute_price_rule()` to use rental pricing when both `start_date` and `end_date` are provided, falling back to standard pricing for non-rental products or when dates are absent.

#### Scenario: Rental price via pricelist
- **WHEN** `_compute_price_rule()` is called with `start_date` and `end_date` for a rent_ok product
- **THEN** the best rental pricing rule is used to compute the price

#### Scenario: Non-rental product unchanged
- **WHEN** `_compute_price_rule()` is called for a product with `rent_ok=False`
- **THEN** standard pricelist pricing logic is used regardless of dates
