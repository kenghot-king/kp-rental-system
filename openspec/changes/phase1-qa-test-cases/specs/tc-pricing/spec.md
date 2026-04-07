## ADDED Requirements

### Requirement: Single-period pricing
The system SHALL correctly price a rental using a single pricing rule.

#### Scenario: TC-PR-001 Daily pricing for exact days
- **WHEN** product has pricing: 100 THB/day, rental duration = 3 days exactly
- **THEN** line price = 300 THB

#### Scenario: TC-PR-002 Daily pricing rounds up partial day
- **WHEN** product has pricing: 100 THB/day, rental duration = 2 days 3 hours
- **THEN** line price = 300 THB (rounds up to 3 days)

#### Scenario: TC-PR-003 Hourly pricing
- **WHEN** product has pricing: 20 THB/hour, rental duration = 5 hours
- **THEN** line price = 100 THB

### Requirement: Best pricing rule selection
The system SHALL automatically select the cheapest pricing rule for a given rental duration.

#### Scenario: TC-PR-004 Weekly rate cheaper than daily for 7 days
- **WHEN** product has daily=100 THB and weekly=500 THB, rental duration = 7 days
- **THEN** system selects weekly rate, line price = 500 THB

#### Scenario: TC-PR-005 Daily rate cheaper than weekly for 3 days
- **WHEN** product has daily=100 THB and weekly=500 THB, rental duration = 3 days
- **THEN** system selects daily rate, line price = 300 THB

#### Scenario: TC-PR-006 Mixed period calculation
- **WHEN** product has daily=100 THB and weekly=500 THB, rental duration = 10 days
- **THEN** system selects cheapest combination (e.g. 1 week + 3 days = 800 THB vs 10 days = 1000 THB)

### Requirement: Pricelist-specific pricing
The system SHALL support different rental pricing per pricelist.

#### Scenario: TC-PR-007 VIP pricelist pricing
- **WHEN** product has default daily=100 THB and VIP pricelist daily=80 THB, customer uses VIP pricelist
- **THEN** rental order uses VIP rate, line price for 3 days = 240 THB

#### Scenario: TC-PR-008 No pricelist-specific pricing falls back
- **WHEN** product has no pricing for customer's pricelist but has default pricing
- **THEN** system uses default pricing

### Requirement: Variant-specific pricing
The system SHALL support different pricing per product variant.

#### Scenario: TC-PR-009 Variant with specific pricing
- **WHEN** product has variant "Large" with daily=150 THB and variant "Small" with daily=100 THB
- **THEN** rental order with "Large" variant uses 150 THB/day

#### Scenario: TC-PR-010 Variant without specific pricing uses template pricing
- **WHEN** product template has daily=100 THB, variant has no specific pricing
- **THEN** variant uses template pricing 100 THB/day

### Requirement: Overnight period pricing
The system SHALL support overnight rental periods with check-in/check-out times.

#### Scenario: TC-PR-011 Overnight pricing applied
- **WHEN** product has overnight recurrence (24hr, pickup_time=14:00, return_time=12:00) priced at 200 THB/night, rental = 2 nights
- **THEN** line price = 400 THB

### Requirement: Product display price
The system SHALL show the first rental pricing on the product card/list.

#### Scenario: TC-PR-012 Display price on product
- **WHEN** product has pricing 100 THB/day
- **THEN** product list/form shows display_price = "100.00 THB / 1 Day"

### Requirement: Rental pricing configuration
The system SHALL allow managing rental period types (recurrences).

#### Scenario: TC-PR-013 Create new recurrence
- **WHEN** admin creates a new recurrence: duration=3, unit=day, name="3-Day"
- **THEN** recurrence is available for product pricing, duration_display = "3 Days"

#### Scenario: TC-PR-014 Deactivate recurrence
- **WHEN** admin deactivates a recurrence
- **THEN** recurrence is no longer available for new pricing rules
