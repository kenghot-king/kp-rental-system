## Context

`payment-channel-metadata` (the predecessor change) delivers the foundation: every rental payment carries `cashier_id`, `approval_code`, and a stable `display_method` string. This change builds the end-of-day workflow on top: a supervisor-facing record per `(cashier, date)`, variance display, payment locking, and reports for paper sign-off.

The business rule is tight: once a supervisor confirms a cashier's day, that day is closed — no edits, no deletes, no new payments. Variance is a reporting number only; no journal entry is posted. Only members of a new `group_rental_supervisor` can confirm or reopen.

Adjacent systems we intentionally do NOT integrate with: Odoo's native bank-statement reconciliation, POS sessions, variance GL posting, multi-branch, and external settlement feeds. These are future phases.

## Goals / Non-Goals

**Goals:**
- Per-cashier-per-date reconciliation record with supervisor-gated lifecycle
- Immutable audit trail: once confirmed, payments are locked against any modification
- Block rule at payment create time so cashiers cannot register payments for already-closed days (including backdated)
- Single-record and period-level reports in both XLSX and PDF
- Dashboard that makes unreconciled `(cashier, date)` tuples discoverable
- Bulk confirm that forces supervisor to complete all actuals before closing in batch

**Non-Goals:**
- Variance → shortage/overage journal entry posting
- Cash float / opening balance tracking
- Per-cashier cash drawer modeling (till session)
- Bank statement matching / acquirer settlement reconciliation
- Company branding / logo on reports (next phase)
- Multi-branch scoping (`res.branch`)
- Automated online payment gateway callbacks
- Any edit-allowed mode on confirmed payments (we lock fully, per decision)

## Decisions

### 1. One record per `(cashier_id, date)`, not per shift or per journal

Each cashier gets exactly one reconciliation record per calendar day. Lines within the record carry the per-method breakdown. A morning + evening shift by the same cashier ends up in one record, not two.

**Why not per shift?** Shift definitions vary by operation; forcing a shift model is overreach. The supervisor reviews the whole day's collection regardless of shift boundaries.

**Why not per journal?** The supervisor's mental model is "Somchai's day" — they hand over a cash envelope and a slip stack that mixes EDC terminals and QR providers. The record is cashier-centric; journals appear inside as rows.

**Enforcement:** unique SQL constraint on `(cashier_id, date)`.

### 2. Lines keyed on `(display_method, journal_id)` — not just journal

Using `(display_method, journal_id)` means that on a single EDC terminal (one journal) accepting VISA + Mastercard + JCB, the supervisor sees three lines with three slip-total entry fields. Their EDC batch report typically breaks out per brand, so this matches what they hold in hand.

**Why stored compute for `display_method`?** Efficient grouping in SQL without joining `account.payment.method.line.name` on every query.

### 3. Payment attach via `reconciliation_id` (M2O), written on confirm

Payments carry `reconciliation_id = NULL` while unreconciled. On `action_confirm`, the reconciliation's `_compute_line_payment_ids` + a write loop assigns `reconciliation_id` onto each matched payment. On `action_reopen`, it's cleared back to NULL.

**Why not a command-driven o2m?** Cleaner to have a real FK on `account.payment`: gives us `reconciliation_id.state` for the lock check, indexable queries ("which payments belong to Somchai's 21-Apr reconciliation?"), and a clear unreconciled-detector (`reconciliation_id IS NULL`).

**Indexing:** index on `(cashier_id, payment_date, reconciliation_id)` — supports both the block check and the smart-filter dashboard query.

### 4. Block rule checks `(cashier_id, payment_date)`, not `create_uid`

The block rule must catch backdated payments created by anyone whose scheduled day is already closed. Checking `create_uid` would let a supervisor backdate into a confirmed day by creating on a cashier's behalf. Checking `(cashier_id, payment_date)` matches exactly what the reconciliation record is keyed on — no gap.

**Where enforced:**
- `account.payment.create()` override (catches direct ORM/API calls)
- `account.payment.write()` override for changes to `cashier_id` or `payment_date` that would move a payment INTO a confirmed day
- `account.payment.register._create_payments()` override (pre-create surface error in wizard UX)

### 5. Full lock on confirmed payments (no allowed-edit fields)

Per the decision to "lock all", once `reconciliation_id.state == 'confirmed'`, the payment's `write()` and `unlink()` raise UserError regardless of which field(s) are being changed. No half-allowed shortcut (e.g. "you can edit `approval_code` but not `amount`").

**Why full lock?** Simpler audit story: "confirmed means frozen." Any correction forces the supervisor to reopen, which is itself tracked. Avoids debates like "can I edit memo but not amount?"

**Cost:** editing a typo in approval code after confirm requires a reopen + re-confirm cycle. Acceptable friction given accounting auditability is the priority.

### 6. `group_rental_supervisor` replaces the earlier `is_rental_supervisor` field

An earlier draft of `payment-channel-metadata` included an `is_rental_supervisor` Boolean on `res.users`. That's been removed from the predecessor change. This change introduces a proper security group instead.

**Why a group, not a field?**
- Groups are the idiomatic Odoo permission mechanism and integrate with `ir.model.access.csv`, record rules, and UI visibility (`groups="..."` on XML views/buttons)
- A Boolean on `res.users` gives us nothing a group doesn't, and forces custom gating code everywhere
- Admins already manage groups via the Users settings UI

**Group definition:** lives in `ggg_rental/security/security.xml`, inherits category from accounting, implies `account.group_account_user` so supervisors can at least view payments/invoices.

### 7. Bulk confirm aborts on any incomplete line (all-or-nothing)

If any selected draft record has any line with null `actual_amount`, the bulk action raises UserError naming the incomplete record(s) and applies no changes. Alternative was silent-skip-to-0 which is ambiguous (was 0 intentional or was it skipped?). Forcing explicit entry keeps the audit trail unambiguous.

### 8. Report stack: PDF via QWeb, XLSX via `xlsxwriter`

- PDF: standard Odoo QWeb template (`ir.actions.report`) with `report_type='qweb-pdf'`
- XLSX: a custom `ir.actions.report`-like controller or a `report.report_xlsx` pattern using `xlsxwriter` (included in Odoo 19's Python deps)

**Why not the OCA `report_xlsx` module?** To avoid an external dependency; Odoo 19 ships `xlsxwriter` natively. A thin controller that generates the file in-memory and returns it is enough for this scope.

### 9. "Needs Reconciliation" smart filter — computed as a view query, not a model

The smart filter surfaces `(cashier_id, payment_date)` tuples with unreconciled payments. Since no reconciliation record yet exists for these tuples, we can't filter the reconciliation model directly.

**Approach:** a PostgreSQL view `rental_daily_reconciliation_needed` selecting distinct `(cashier_id, payment_date)` from `account.payment WHERE reconciliation_id IS NULL AND state = 'posted' AND cashier_id IS NOT NULL`. Exposed as a read-only Odoo model with a "Create Reconciliation" server action that opens a pre-populated draft.

**Why not a computed field on reconciliation?** The whole point of the smart filter is to show tuples that *don't yet have a record*. A model view is the natural fit.

### 10. Period report 90-day cap — hard stop

Enforced at the controller / server-action level before any data fetch. UserError named with clear guidance. No silent truncation.

**Why cap at 90?** Beyond a quarter, period reconciliation reports tend to be management-summary territory rather than operational — that's a different use case (future BI dashboard). The cap also prevents accidental multi-year exports dragging the server.

## Risks / Trade-offs

- **[Risk] `cashier_id` retroactively changed via sudo or migration** — could cause a payment to suddenly match a confirmed reconciliation from a different cashier. → Mitigation: `write()` override also checks the *destination* `(cashier_id, payment_date)` against confirmed reconciliations, not just the current one. Tests cover this.
- **[Risk] Late payment arrives through admin sudo after confirm** — bypasses the `create()` check entirely via `sudo()`. → Accepted: sudo is an explicit admin escape hatch; auditable via payment's create_date > reconciliation's confirmed_at. Not in scope to fully block admin overrides.
- **[Risk] Line recompute on draft reconciliation is slow if cashier has many payments in a day** — unlikely to matter at rental-business volume (tens of payments/day/cashier) but flagged. → Accepted; revisit only if an operational report complains.
- **[Risk] Bulk confirm abort behavior surprises supervisors** — if 4/5 records are complete and 1 isn't, the fix-it-and-retry loop is slightly longer than a per-record confirm. → Accepted: alternative (silent skip or confirm-partials) introduces ambiguity. The error message will name which record is incomplete so the supervisor knows exactly where to go.
- **[Risk] Period report at exactly 90 days works; at 91 fails** — edge-case confusion. → Mitigation: inclusive check `(date_to - date_from).days <= 90`; document in the UserError message: "date range exceeds 90 days (limit is 90 days inclusive)".
- **[Trade-off] No GL variance posting means finance must track shortage/overage externally (paper/spreadsheet) until the next phase.** → Accepted per business decision. Next phase adds automated posting without structural rework.
- **[Trade-off] Using a PostgreSQL view for "Needs Reconciliation" is lightweight but opaque to ORM-only developers.** → Acceptable: pattern is common in Odoo (see `hr.leave.report`, `sale.report`, etc.) and well-documented.
- **[Trade-off] Full payment lock forces reopen for trivial corrections** (typo in approval code). → Accepted per "lock all" decision; supervisors will use the reopen flow for corrections, and the audit chatter makes it traceable.
- **[Open question deferred] What if a cashier permanently leaves and has lingering unreconciled payments?** → Out of scope for this change. Future: a supervisor re-attribution action that transfers payments to a different cashier (with audit trail).
