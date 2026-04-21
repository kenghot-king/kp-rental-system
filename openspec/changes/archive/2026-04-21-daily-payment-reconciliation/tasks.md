## 1. Security Group

- [x] 1.1 Add `group_rental_supervisor` in `ggg_rental/security/security.xml` (category: Accounting; implied: `account.group_account_user`)
- [x] 1.2 Add `ir.model.access.csv` entries — full CRUD for supervisors, read-only for `base.group_user` on `rental.daily.reconciliation` and `rental.daily.reconciliation.line`
- [x] 1.3 Register security files in `__manifest__.py` `data` list (before model data)

## 2. Reconciliation Models

- [x] 2.1 Create `ggg_rental/models/rental_daily_reconciliation.py` with `rental.daily.reconciliation` model (inherit `mail.thread`)
- [x] 2.2 Add fields: `date` (Date, required, default today), `cashier_id` (M2O res.users, required), `state` (Selection draft/confirmed, default draft, tracked), `note` (Text), `confirmed_by` (M2O res.users, readonly), `confirmed_at` (Datetime, readonly), `reopened_by` (M2O res.users, readonly), `reopened_at` (Datetime, readonly)
- [x] 2.3 Add `line_ids` One2many, `expected_total` / `actual_total` / `variance_total` computed monetary fields
- [x] 2.4 Add SQL unique constraint on `(cashier_id, date)`
- [x] 2.5 Add `currency_id` related/computed so monetary fields render correctly
- [x] 2.6 Create `rental.daily.reconciliation.line` model with `reconciliation_id`, `display_method` (Char), `journal_id` (M2O), `expected_amount` (computed), `actual_amount` (Monetary, entered), `variance` (computed), `payment_ids` (One2many)
- [x] 2.7 Register new models in `ggg_rental/models/__init__.py`

## 3. Payment Model Extension (linkage + lock + block)

- [x] 3.1 Add `reconciliation_id` M2O → `rental.daily.reconciliation` on `account.payment` (in the existing extension file from change 1), with index
- [x] 3.2 Override `account.payment.create()` — if `(cashier_id, payment_date)` matches a confirmed reconciliation, raise UserError naming the reconciliation
- [x] 3.3 Override `account.payment.write()` — two checks: (a) if current `reconciliation_id.state == 'confirmed'`, raise UserError (lock all); (b) if `cashier_id` or `payment_date` are being changed and the new tuple matches a confirmed reconciliation, raise UserError (no cheating into closed days)
- [x] 3.4 Override `account.payment.unlink()` — if any record has `reconciliation_id.state == 'confirmed'`, raise UserError

## 4. Register Wizard Block

- [x] 4.1 Override `account.payment.register._create_payments` (Odoo 19 name) to pre-check `(env.user, payment_date)` against confirmed reconciliations and raise UserError with a clear message + reconciliation name before the payment is created
- [x] 4.2 Ensure the error message text names the reconciliation's supervisor so cashier knows who to ask for reopen

## 5. State Transitions (actions)

- [x] 5.1 Implement `action_confirm` on `rental.daily.reconciliation`: enforce `group_rental_supervisor`; validate every line has non-null `actual_amount`; set state, confirmed_by, confirmed_at; write `reconciliation_id` onto each line's `payment_ids`; post chatter message
- [x] 5.2 Implement `action_reopen`: enforce `group_rental_supervisor`; set state=draft, reopened_by, reopened_at; clear `reconciliation_id` on all attached payments; post chatter message
- [x] 5.3 Implement server action `action_confirm_multi` (bulk confirm): if any selected record has any line with null `actual_amount`, raise UserError naming offending records; else iterate `action_confirm`

## 6. Reconciliation Line Recompute

- [x] 6.1 On reconciliation creation (via smart filter or manual), auto-populate `line_ids` by grouping attached payments on `(display_method, journal_id)` — either `@api.model_create_multi` or a helper `_rebuild_lines()` method
- [x] 6.2 Expose `_rebuild_lines()` as a "Refresh Lines" button on the form (draft state only) so supervisors can pick up late payments before confirming

## 7. Needs-Reconciliation Smart Filter

- [x] 7.1 Create PostgreSQL view model `rental.daily.reconciliation.needed` (similar pattern to `sale.report`) selecting `(cashier_id, payment_date)` tuples where posted payments exist with `reconciliation_id IS NULL`
- [x] 7.2 Add tree view + search view for the needed-model; include a "Create Reconciliation" server action that instantiates a draft `rental.daily.reconciliation` for the selected tuple and calls `_rebuild_lines()`

## 8. Dashboard Views

- [x] 8.1 Tree view for `rental.daily.reconciliation` (columns: date, cashier, expected_total, actual_total, variance_total, state)
- [x] 8.2 Form view with header buttons (Confirm / Reopen), line breakdown, chatter
- [x] 8.3 Search view with filters: State, Cashier, Date range, Has Variance, Needs Reconciliation (links to the needed-model view)
- [x] 8.4 Menu: `Rental → Daily Reconciliation` (supervisor group visibility; moved from Accounting to Rental app)
- [x] 8.5 Inherit `account.payment` form to display `reconciliation_id` and reconciliation state badge

## 9. Reports — Single Record

- [x] 9.1 QWeb PDF template `ggg_rental/report/reconciliation_single_pdf.xml` — header, line table, totals, signature block (cashier/supervisor/date labeled lines)
- [x] 9.2 Register `ir.actions.report` for the PDF, bound to `rental.daily.reconciliation`
- [x] 9.3 XLSX controller or server action that builds the single-record XLSX using `xlsxwriter`, returns download response
- [x] 9.4 "Print XLSX" button on reconciliation form

## 10. Reports — Period

- [x] 10.1 Wizard `rental.daily.reconciliation.period.report.wizard` (Transient Model) with fields: date_from, date_to, cashier_ids (M2M optional filter), format (selection: xlsx/pdf)
- [x] 10.2 Wizard action validates `(date_to - date_from).days <= 90`; raises UserError with cap message if exceeded
- [x] 10.3 Wizard generates XLSX — rows grouped/sorted by cashier then date; columns: date, cashier, expected, actual, variance, state
- [x] 10.4 Wizard generates PDF — QWeb template with one reconciliation per page + signature blocks
- [x] 10.5 Menu / toolbar action from the dashboard: "Export Period Report"

## 11. Manifest & Data

- [x] 11.1 Add all XML and Python files to `ggg_rental/__manifest__.py` data list in correct order (security → data → views → actions → menus → reports)
- [x] 11.2 Bump module version

## 12. Verification

- [ ] 12.1 Create a draft reconciliation for cashier A on 2026-04-21 with one cash line; enter actual; confirm — verify payment's `reconciliation_id` is set and state = confirmed (manual test — deferred to user)
- [ ] 12.2 Attempt to edit the confirmed reconciliation's payment amount — verify UserError (manual test — deferred to user)
- [ ] 12.3 Attempt to register a new payment as cashier A for 2026-04-21 — verify UserError names the reconciliation (manual test — deferred to user)
- [ ] 12.4 Supervisor reopens the reconciliation — verify payment is unlocked and editable (manual test — deferred to user)
- [ ] 12.5 Non-supervisor user opens the reconciliation — verify read-only, no confirm/reopen buttons visible (manual test — deferred to user)
- [ ] 12.6 Create 5 drafts; one has null actual_amount; bulk confirm — verify all-or-nothing error (manual test — deferred to user)
- [ ] 12.7 Period report at 90 days succeeds, at 91 days raises UserError (manual test — deferred to user)
- [ ] 12.8 Needs-reconciliation smart filter shows tuples with unreconciled payments and excludes confirmed days (manual test — deferred to user)
- [ ] 12.9 Backdated payment for a confirmed day is blocked (manual test — deferred to user)
- [ ] 12.10 XLSX and PDF single-record prints produce the expected content including signature block (manual test — deferred to user)
