## Why

After `payment-channel-metadata` ships, every rental payment carries cashier attribution, channel classification, and approval-code audit data. The business still needs an end-of-day workflow where a supervisor can confirm each cashier's daily collection, expose variances between system-expected and physically-counted amounts, and produce a signed report. Today this is done on paper outside Odoo — no audit trail, no linkage between the signed sheet and the payment records. This change delivers the reconciliation record, supervisor-gated confirm/reopen flow, payment locking, and XLSX+PDF reports (single record + period summary).

## What Changes

- Add `rental.daily.reconciliation` model (with `mail.thread` audit) — one record per `(cashier_id, date)` tuple; state `draft`/`confirmed`; stores totals and supervisor attribution
- Add `rental.daily.reconciliation.line` model — one line per `(display_method, journal_id)` slice within a reconciliation; carries expected amount (computed from attached payments), supervisor-entered actual amount, and variance
- Add `reconciliation_id` Many2one on `account.payment` linking each payment to its parent reconciliation (NULL when unreconciled)
- Introduce `group_rental_supervisor` security group in `ggg_rental` — required for create/confirm/reopen actions on reconciliations; all other users have read-only access to reconciliation records
- Supervisor action `action_confirm` — transitions draft → confirmed, writes `reconciliation_id` onto every payment in scope, logs to chatter
- Supervisor action `action_reopen` — transitions confirmed → draft, clears `reconciliation_id` from payments, records reopener identity, logs to chatter
- Bulk confirm from list view — **aborts** with error if any selected record has any line with unset `actual_amount`
- Payment lock — when `reconciliation_id.state == 'confirmed'`, the payment record's `write()` and `unlink()` are blocked entirely (lock all fields)
- Payment creation block — when a confirmed reconciliation exists for `(cashier_id, payment_date)`, creating a new payment for that pair (including backdated payments) is blocked with a UserError pointing the supervisor to reopen
- Dashboard with smart "Needs Reconciliation" filter — surfaces `(cashier, date)` combos that have at least one unreconciled `posted` payment
- Single-record XLSX report (print button on form)
- Single-record PDF report (print button on form, includes cashier/supervisor/date signature block — no company branding this phase)
- Period XLSX report — multi-record export driven by dashboard filters, date range capped at 90 days
- Period PDF report — same capping, suitable for paper sign-off batches
- **BREAKING (internal, pre-release):** Change 1 `payment-channel-metadata` was edited to drop `is_rental_supervisor` on `res.users`; supervisor identification now uses `group_rental_supervisor` introduced by this change

## Capabilities

### New Capabilities
- `daily-payment-reconciliation`: Per-cashier-per-day reconciliation records, supervisor-gated confirm/reopen workflow, payment locking and block rules, and XLSX+PDF single-record and period reports

### Modified Capabilities
<!-- None — this change does not alter requirements of any existing spec.
     The dependency on payment-channel-metadata is structural (uses its fields)
     but does not modify that spec's requirements. -->

## Impact

- `rental.daily.reconciliation` model — new
- `rental.daily.reconciliation.line` model — new
- `account.payment` model — new `reconciliation_id` M2O + `write`/`unlink`/`create` overrides implementing the lock and block rules
- `account.payment.register` wizard — create-time check replicating the block rule to surface the error before the wizard persists
- `ggg_rental` security — new `group_rental_supervisor`, ACL rules for the two new models (full CRUD for supervisors, read-only for others)
- Views — list view, form view, search view, and kanban (optional) for reconciliation; inherit on `account.payment` to show `reconciliation_id` and state
- Menu — `Accounting → Rental → Daily Reconciliation`
- Reports — four new report definitions (single XLSX, single PDF, period XLSX, period PDF); relies on `xlsxwriter` or `report_xlsx` convention (to be picked in design)
- Module manifest — new Python model files, XML views, XML reports, security CSV/XML, data file entries
- Runtime cost — block rules add a `SELECT` query on payment create/write; indexed by `(cashier_id, payment_date)` on the reconciliation table to keep it cheap
