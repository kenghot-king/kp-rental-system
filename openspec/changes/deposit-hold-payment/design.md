## Context

Odoo's `account.payment` has four standard states: `draft`, `posted`, `cancel`, `sent`. There is no "pending authorization" concept. When a payment is posted, it creates a journal entry and reconciles against the invoice immediately. For credit card pre-authorization (hold), we need a state where the payment record exists and stores authorization metadata but creates **no journal entry** — the hold is not real money received.

The deposit invoice (`[Deposit] Product`) is a separate `account.move` from the rental invoice, created at order confirmation. This separation allows independent payment flows for rent vs deposit.

Reference: `documents/CR/hold_payment.md`

## Goals / Non-Goals

**Goals:**
- Track credit card pre-authorization as an `account.payment` in `processing` state with no journal entry
- Store `approval_code` (pre-auth code) and `ref_2` (card reference) on the hold payment
- Allow staff to Forfeit (post + reconcile) or Unhold (release + eventually cancel) the hold
- Preserve cancelled hold payment records for audit and reporting
- Block HLD journal from being used on rental invoices

**Non-Goals:**
- Integration with actual card processor / EDC terminal API (approval code entered manually)
- Multi-currency hold payments
- Partial hold forfeitures
- Modifying the EDC (normal payment) flow — it remains standard Odoo

## Decisions

### 1. Custom `processing` state on `account.payment`
Use a new selection value `processing` added via `_inherit` rather than repurposing `draft`. Reason: `draft` in Odoo implies a record that can be freely edited or deleted. We need a distinct state that signals "hold is active, do not post or delete". This also lets us add a guard on `action_post` specifically for `is_deposit_hold=True` records.

Alternative considered: store hold state on the invoice only, skip creating a payment record. Rejected — losing the payment record loses `approval_code`, `ref_2`, and the audit trail.

### 2. Cancel instead of delete on unhold completion
When the credit note is reconciled after return, the hold payment is set to `cancel` state rather than `unlink()`-ed. This preserves the `approval_code`, `ref_2`, amount, and timestamps for reporting. A cancelled `is_deposit_hold` payment has no journal entry so it has no financial impact.

Alternative considered: delete the record for cleanliness. Rejected — the approval code is the only trace of the pre-authorization and is needed for card disputes.

### 3. `deposit_hold_state` computed on `account.move`
A computed field `deposit_hold_state` on the deposit invoice (`'none'` / `'hold'`) is derived from whether a related `account.payment` with `is_deposit_hold=True` and `state='processing'` exists. This drives the UI badge and button visibility. It does NOT affect Odoo's native `payment_state` computation (which is based on reconciled journal entries only).

### 4. Forfeit wizard for date capture
A minimal wizard (`account.payment.forfeit.wizard`) captures the forfeiture date (default: today). This is needed because the customer may not show up on a specific date that differs from today, and the forfeiture date appears on the printed receipt. The wizard calls `action_forfeit(date)` on the invoice.

### 5. CN guard on `sale.order.line._create_deposit_credit_note`
The method that auto-creates a credit note when items are returned is guarded to skip execution when `deposit_hold_state == 'hold'`. This prevents a CN from being created while the hold is still active (which would reconcile the invoice prematurely). The guard is safe because Unhold sets `deposit_hold_state` to `none` before the return processing continues.

## Risks / Trade-offs

- [Odoo upgrade] Custom `processing` state on `account.payment` may conflict with future Odoo core states → Use `_inherit` selection override; test on each upgrade
- [Reporting] Cancelled hold payments mixed with cancelled normal payments in `account.payment` list → Filter by `is_deposit_hold=True` in report views
- [Concurrency] Staff clicks Forfeit and CN is triggered simultaneously → The `deposit_hold_state == 'hold'` guard on CN creation prevents double-reconciliation; forfeit sets state to `posted` atomically
- [Unhold without return] Staff clicks Unhold but customer never returns → Invoice stays `not_paid`, hold payment stays `draft` indefinitely → UI should warn; no automated resolution needed now

## Migration Plan

1. Install updated `ggg_rental` module — migrations add `for_hold` to `account.journal`, `is_deposit_hold` + `processing` state to `account.payment`
2. Existing posted payments are unaffected (no `is_deposit_hold`)
3. No data migration needed — feature only applies to new holds after install
4. Rollback: remove `processing` state value and `is_deposit_hold` field; any in-flight hold payments in `processing` state would need manual resolution before rollback

## Open Questions

- Should the Forfeit receipt print automatically after forfeiture, or require manual staff action?
- Should unholding require a supervisor PIN (similar to the paid-order lock feature)?
