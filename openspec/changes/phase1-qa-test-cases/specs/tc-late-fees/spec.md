## ADDED Requirements

### Requirement: Late fee calculation with grace period
The system SHALL calculate late fees only when the return exceeds the grace period (min_extra_hour), using hourly and daily rates.

#### Scenario: TC-LF-001 Return on time — no late fee
- **WHEN** rental return_date=2026-04-12 09:00, actual return at 2026-04-12 08:30
- **THEN** no delay line is created on the SO

#### Scenario: TC-LF-002 Return within grace period — no late fee
- **WHEN** min_extra_hour=2, return_date=2026-04-12 09:00, actual return at 2026-04-12 10:30 (1.5 hrs late)
- **THEN** no delay line is created (within 2-hour grace)

#### Scenario: TC-LF-003 Return after grace period — late fee created
- **WHEN** min_extra_hour=2, return_date=2026-04-12 09:00, actual return at 2026-04-12 14:00 (5 hrs late), extra_hourly=50 THB/hr, extra_daily=0
- **THEN** delay line created with price = 5 × 50 = 250 THB

#### Scenario: TC-LF-004 Late by days and hours
- **WHEN** return_date=2026-04-12 09:00, actual return at 2026-04-14 14:00 (2 days 5 hrs late), extra_hourly=50, extra_daily=200
- **THEN** delay line created with price = (2 × 200) + (5 × 50) = 650 THB

#### Scenario: TC-LF-005 Late fee uses company delay product
- **WHEN** company.extra_product is set to "Late Return Fee" service product
- **THEN** delay line uses that product

#### Scenario: TC-LF-006 Delay product auto-created if not configured
- **WHEN** company.extra_product is not set and a late return occurs
- **THEN** system auto-creates a "Rental Delay Cost" service product with default_code="DELAY"

### Requirement: Product-level late fee override
The system SHALL allow per-product hourly/daily late fees that override company defaults.

#### Scenario: TC-LF-007 Product-specific late fees
- **WHEN** product extra_hourly=100 (company default=50), return is 3 hours late
- **THEN** delay line uses product rate: 3 × 100 = 300 THB

#### Scenario: TC-LF-008 Product without override uses company default
- **WHEN** product extra_hourly not set (0), company extra_hour=50, return is 3 hours late
- **THEN** delay line uses company rate: 3 × 50 = 150 THB

### Requirement: Grace period configuration
The system SHALL allow configuring the grace period (min_extra_hour) in rental settings.

#### Scenario: TC-LF-009 Change grace period
- **WHEN** admin changes min_extra_hour from 2 to 4 in Settings
- **THEN** subsequent returns within 4 hours of return_date do not incur late fees
