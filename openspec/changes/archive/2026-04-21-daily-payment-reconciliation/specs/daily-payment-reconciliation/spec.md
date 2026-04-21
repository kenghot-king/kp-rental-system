## ADDED Requirements

### Requirement: Reconciliation record scope and uniqueness

The system SHALL provide a `rental.daily.reconciliation` model such that at most one record exists for any `(cashier_id, date)` tuple. A reconciliation record SHALL aggregate all `posted` `account.payment` records matching its cashier and date through one `rental.daily.reconciliation.line` per `(display_method, journal_id)` slice.

#### Scenario: Unique (cashier, date) pair
- **WHEN** a user attempts to create a second `rental.daily.reconciliation` for a cashier and date already having a record
- **THEN** the system SHALL raise a unique constraint error and refuse the create

#### Scenario: Lines grouped by (display_method, journal)
- **WHEN** a reconciliation record is created for Cashier Somchai on 2026-04-21 and Somchai has payments under (VISA, EDC-KBank-Silom-T1), (Mastercard, EDC-KBank-Silom-T1), (Cash, Cash)
- **THEN** the reconciliation SHALL contain three lines, one per `(display_method, journal_id)` pair, each with `expected_amount` equal to the sum of its payments

#### Scenario: No payments means no record
- **WHEN** a cashier has zero posted payments for a given date
- **THEN** the system SHALL NOT require or auto-create a reconciliation record for that `(cashier, date)`

### Requirement: Reconciliation state machine

The system SHALL track `state` on each `rental.daily.reconciliation` with exactly two values: `draft` (default, editable by supervisor) and `confirmed` (locked from further edits to lines; payments linked). Transitions SHALL be gated to members of `group_rental_supervisor`.

#### Scenario: Supervisor confirms a draft
- **WHEN** a user in `group_rental_supervisor` invokes `action_confirm` on a draft reconciliation where every line has an `actual_amount` entered
- **THEN** the state SHALL transition to `confirmed`, `confirmed_by` SHALL equal the acting user, `confirmed_at` SHALL equal the current datetime, and each associated payment's `reconciliation_id` SHALL be written to the reconciliation's ID

#### Scenario: Non-supervisor cannot confirm
- **WHEN** a user who is not in `group_rental_supervisor` invokes `action_confirm`
- **THEN** the system SHALL raise an access error and the state SHALL remain `draft`

#### Scenario: Supervisor reopens a confirmed reconciliation
- **WHEN** a user in `group_rental_supervisor` invokes `action_reopen` on a confirmed reconciliation
- **THEN** the state SHALL transition to `draft`, `reopened_by` SHALL equal the acting user, `reopened_at` SHALL equal the current datetime, and every associated payment's `reconciliation_id` SHALL be cleared

#### Scenario: Audit trail on transitions
- **WHEN** `action_confirm` or `action_reopen` completes successfully
- **THEN** a chatter message SHALL be posted on the reconciliation record describing the action, the acting user, and the timestamp

### Requirement: Bulk confirm aborts on incomplete actuals

The system SHALL provide a "Confirm Selected" multi-record action in the reconciliation list view. The action SHALL abort with a UserError — performing no state change on any selected record — if any selected reconciliation has at least one line where `actual_amount` has not been entered (is null).

#### Scenario: All selected records complete
- **WHEN** a supervisor selects five draft reconciliations where every line has an `actual_amount` and invokes "Confirm Selected"
- **THEN** all five SHALL transition to `confirmed`

#### Scenario: One selected record incomplete
- **WHEN** a supervisor selects five draft reconciliations and one of them has a line with null `actual_amount`
- **THEN** the action SHALL raise a UserError identifying the incomplete record(s), and NONE of the five SHALL change state

### Requirement: Payment lock when reconciliation is confirmed

The system SHALL block all modification of `account.payment` records whose `reconciliation_id` points to a reconciliation in state `confirmed`. Both `write()` and `unlink()` SHALL raise a UserError regardless of which fields are being written.

#### Scenario: Edit blocked on locked payment
- **WHEN** a user attempts to modify any field (amount, journal, method, references, approval code, date, cashier) on a payment whose reconciliation is confirmed
- **THEN** the system SHALL raise a UserError and make no change

#### Scenario: Delete blocked on locked payment
- **WHEN** a user attempts to delete a payment whose reconciliation is confirmed
- **THEN** the system SHALL raise a UserError

#### Scenario: Unlock after reopen
- **WHEN** a supervisor reopens the reconciliation containing a locked payment
- **THEN** subsequent edits to that payment SHALL succeed (its `reconciliation_id` has been cleared by the reopen action)

### Requirement: Payment creation block for confirmed (cashier, date)

The system SHALL block the creation of any `account.payment` record whose `(cashier_id, payment_date)` matches an existing `rental.daily.reconciliation` in state `confirmed`. The check SHALL apply to direct `create()` calls, to `account.payment.register` wizard `_create_payments` flows, and to backdated payments (where `payment_date` is earlier than today).

#### Scenario: New payment for confirmed day blocked
- **WHEN** a cashier registers a new payment via the Pay wizard and their `(env.user, payment_date)` matches a confirmed reconciliation
- **THEN** the wizard SHALL raise a UserError whose message names the confirmed reconciliation and asks the supervisor to reopen it before retrying

#### Scenario: Backdated payment blocked
- **WHEN** any user creates an `account.payment` on today's calendar date with `payment_date` set to an earlier date, and a confirmed reconciliation exists for `(payment.cashier_id, payment.payment_date)`
- **THEN** the system SHALL raise a UserError and NOT persist the payment

#### Scenario: No block when reconciliation is draft
- **WHEN** the matching reconciliation exists but is in `draft` state
- **THEN** payment creation SHALL succeed

### Requirement: Reconciliation line totals and variance

The system SHALL compute each line's `expected_amount` as the sum of the amounts of payments attached to the line, the line's `variance` as `actual_amount - expected_amount`, and the parent reconciliation's `expected_total`, `actual_total`, and `variance_total` as the sums of the corresponding line fields. Variance SHALL NOT produce a journal entry; it is data-only.

#### Scenario: Expected amount recomputes from payments
- **WHEN** additional unreconciled payments are added to a draft reconciliation's scope and the record is refreshed
- **THEN** the affected line's `expected_amount` SHALL reflect the new sum

#### Scenario: Variance computed after actual entered
- **WHEN** a supervisor enters `actual_amount = 5640` on a line whose `expected_amount = 5640`
- **THEN** `variance` SHALL equal 0 and the reconciliation's `variance_total` SHALL reflect this line's zero contribution

#### Scenario: No GL impact on confirm
- **WHEN** a reconciliation is confirmed with a non-zero `variance_total`
- **THEN** the system SHALL NOT create any `account.move` or journal entry as a result of the confirmation

### Requirement: Reconciliation access control

The system SHALL restrict create, confirm, reopen, and delete of `rental.daily.reconciliation` records (and write on `rental.daily.reconciliation.line`) to users in `group_rental_supervisor`. All other authenticated users SHALL have read-only access to reconciliation records and lines.

#### Scenario: Non-supervisor can view but not edit
- **WHEN** a user without `group_rental_supervisor` membership opens a reconciliation record
- **THEN** the form SHALL render in read-only mode and no confirm/reopen/save action SHALL be available

#### Scenario: Non-supervisor cannot create reconciliation
- **WHEN** a user without `group_rental_supervisor` membership attempts to create a `rental.daily.reconciliation` record
- **THEN** the system SHALL raise an access error

### Requirement: Needs-reconciliation dashboard

The system SHALL provide a dashboard view for reconciliations with filters for `state`, `date` range, `cashier_id`, and a smart "Needs Reconciliation" filter. The smart filter SHALL surface `(cashier_id, payment_date)` tuples that have at least one `posted` `account.payment` with `reconciliation_id` unset.

#### Scenario: Smart filter surfaces unreconciled tuples
- **WHEN** Cashier Malee has two posted payments on 2026-04-21 with `reconciliation_id` unset, and no reconciliation record exists for that pair
- **THEN** activating the "Needs Reconciliation" smart filter SHALL display a row representing `(Malee, 2026-04-21)`, with a "Create" action that opens a pre-populated draft reconciliation

#### Scenario: Filter excludes already-reconciled
- **WHEN** a cashier's day is already represented by a `confirmed` reconciliation
- **THEN** that `(cashier, date)` SHALL NOT appear under the "Needs Reconciliation" filter

### Requirement: Single-record reports (XLSX and PDF)

The system SHALL provide a printable XLSX and a printable PDF report for a single `rental.daily.reconciliation` record. The PDF SHALL include a signature block with labeled lines for cashier signature, supervisor signature, and date. Company logo or branded styling is NOT required in this phase.

#### Scenario: Single XLSX print
- **WHEN** a user clicks "Print XLSX" on a reconciliation form
- **THEN** an XLSX file SHALL download containing the header (cashier, date, state, totals) and one data row per line with columns for display method, journal, expected, actual, and variance

#### Scenario: Single PDF print with signature block
- **WHEN** a user clicks "Print PDF" on a reconciliation form
- **THEN** a PDF file SHALL be generated containing the reconciliation summary, line breakdown, and a signature block with three labeled lines (cashier, supervisor, date)

### Requirement: Period reports (XLSX and PDF, 90-day cap)

The system SHALL provide XLSX and PDF period summary reports driven by the dashboard's current filter set (date range + cashier filter). The system SHALL reject requests whose effective date range exceeds 90 days.

#### Scenario: Period XLSX within cap
- **WHEN** a supervisor selects a 30-day date range and invokes "Export Period XLSX"
- **THEN** an XLSX file SHALL download with one row per reconciliation record (columns: date, cashier, expected total, actual total, variance total, state) grouped or sorted by cashier then date

#### Scenario: Period report rejected above cap
- **WHEN** a supervisor sets a 120-day date range and invokes any period report
- **THEN** the system SHALL raise a UserError stating the 90-day maximum and SHALL NOT generate the report

#### Scenario: Period PDF within cap
- **WHEN** a supervisor invokes "Export Period PDF" within the 90-day cap
- **THEN** a PDF SHALL be generated suitable for paper sign-off, one reconciliation per page with its signature block
