## ADDED Requirements

### Requirement: Cancelled hold payments retained for audit
Hold payments that are cancelled after a return SHALL remain in the database with `state='cancel'`. The system SHALL NOT delete these records.

#### Scenario: Cancelled hold payment queryable
- **WHEN** querying `account.payment` filtered by `is_deposit_hold=True` and `state='cancel'`
- **THEN** all completed (returned) hold payment records are returned
- **THEN** each record retains `approval_code`, `ref_2`, `amount`, `date`, `partner_id`, and `journal_id`

### Requirement: Hold payment links back to deposit invoice
Each hold payment SHALL be navigable from the deposit invoice via a smart button or related field.

#### Scenario: Hold payment visible from invoice
- **WHEN** viewing a deposit invoice that has or had a hold payment
- **THEN** a smart button or related list shows the associated `account.payment` record(s)

### Requirement: Hold payments filterable by state for reporting
Staff SHALL be able to filter `account.payment` records by `is_deposit_hold=True` to view all hold-type payments and their outcomes (processing, posted, cancelled).

#### Scenario: Filter by is_deposit_hold
- **WHEN** filtering payments by `is_deposit_hold=True`
- **THEN** only hold-type payments are returned, grouped by state to show active holds, forfeited holds, and released (cancelled) holds
