## ADDED Requirements

### Requirement: Day count uses calendar-date difference

The system SHALL compute the rental day count as the difference between the return date's calendar date and the pickup date's calendar date, ignoring the time-of-day components.

#### Scenario: Multi-day rental with end-of-day return

- **WHEN** a rental order has `rental_start_date` = Apr 29 09:00 and `rental_return_date` = May 3 23:59
- **THEN** the day count used for pricing SHALL be 4 (not 5)
- **AND** the order's daily-tier price SHALL be charged for exactly 4 days

#### Scenario: Multi-day rental with same time-of-day return

- **WHEN** a rental order has `rental_start_date` = Apr 29 09:00 and `rental_return_date` = May 3 09:00
- **THEN** the day count SHALL be 4

#### Scenario: Rental crossing midnight by a few hours

- **WHEN** a rental order has `rental_start_date` = Apr 29 09:00 and `rental_return_date` = Apr 30 01:00
- **THEN** the day count SHALL be 1
- **AND** the order SHALL be priced as a 1-day rental

#### Scenario: Same calendar date rental

- **WHEN** a rental order has `rental_start_date` = Apr 29 09:00 and `rental_return_date` = Apr 29 17:00
- **THEN** the day count SHALL be 0
- **AND** pricing SHALL fall through to the hourly tier or the 1-day fallback (see separate requirements)

### Requirement: Display fields match billing model

The system SHALL compute `sale.order.duration_days` and `sale.order.remaining_hours` so that the displayed values match the values used for pricing.

#### Scenario: Multi-day order shows day count only

- **WHEN** the rental spans 4 calendar dates (Apr 29 → May 3)
- **THEN** `duration_days` SHALL be 4
- **AND** `remaining_hours` SHALL be 0
- **AND** the form view SHALL render "4 days" without an "and X hours" suffix

#### Scenario: Sub-day order shows hour count only

- **WHEN** the rental's pickup and return are on the same calendar date
- **THEN** `duration_days` SHALL be 0
- **AND** `remaining_hours` SHALL be the ceiling of the elapsed hours
- **AND** the form view SHALL render only the hour count (no "X days and" prefix)

#### Scenario: Cross-midnight rental shows day count only

- **WHEN** the rental crosses midnight by any duration (e.g., Apr 29 09:00 → Apr 30 01:00)
- **THEN** `duration_days` SHALL be 1
- **AND** `remaining_hours` SHALL be 0

### Requirement: Sub-day rentals use hourly tier when available

When the day count is 0 (same calendar date), the system SHALL price the rental using the product's hourly pricing tier through the existing greedy algorithm.

#### Scenario: Same-day rental with hourly tier

- **WHEN** a same-day rental is placed for a product that has an Hourly pricing tier configured
- **THEN** the order SHALL be priced as `ceil(elapsed_hours) * hourly_rate`

### Requirement: Sub-day rentals fall back to one day when no hourly tier exists

When the day count is 0 and the product has no hourly tier (smallest configured tier is one day or larger), the system SHALL bill one unit of the smallest available tier as a minimum.

#### Scenario: Same-day rental with daily-only product

- **WHEN** a same-day rental is placed for a product that has only a Daily tier (no Hourly)
- **THEN** the order SHALL be priced as one Daily tier unit
- **AND** the order SHALL NOT be priced at zero

#### Scenario: Same-day rental with weekly-only product

- **WHEN** a same-day rental is placed for a product whose smallest tier is Weekly
- **THEN** the order SHALL be priced as one Weekly tier unit (the smallest available)

### Requirement: Week count derived from day count

The system SHALL compute the rental week count as `ceil(day_count / 7)` and the day count itself follows the calendar-date-difference rule.

#### Scenario: Two-week rental

- **WHEN** the rental spans 14 calendar dates
- **THEN** the week count used by greedy pricing SHALL be 2

#### Scenario: One-and-a-half-week rental

- **WHEN** the rental spans 11 calendar dates
- **THEN** the day count SHALL be 11
- **AND** greedy pricing SHALL combine 1 week + 4 days (rather than 2 weeks)

### Requirement: Confirmed orders are not re-priced

The system SHALL NOT retroactively re-price sale orders that have already been confirmed when this change takes effect; the new computation applies only to new and draft orders.

#### Scenario: Confirmed order keeps its stored price

- **WHEN** an order was confirmed before this change with `price_unit` reflecting the old day-count rule
- **AND** the module is upgraded
- **THEN** the order's `price_unit` SHALL remain unchanged
