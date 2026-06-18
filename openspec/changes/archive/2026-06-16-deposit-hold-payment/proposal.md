## Why

King Power's rental operation accepts security deposits via credit card pre-authorization (hold), not an actual charge. The standard Odoo payment flow has no concept of a "held but not posted" payment — registering any payment immediately posts a journal entry and marks the invoice as paid. We need a hold payment mechanism that tracks the pre-auth without financial impact until the hold is either forfeited (customer no-show) or released (customer returns equipment).

## What Changes

- New `for_hold` boolean on `account.journal` to designate the HLD journal as a hold-type journal
- New `is_deposit_hold` boolean on `account.payment` to mark a payment as a credit hold
- New custom `processing` state on `account.payment` — hold is active, no journal entry created
- Deposit invoice gains `deposit_hold_state` computed field (`none` / `hold`) driving UI badge and action buttons (Unhold, Forfeit)
- **Forfeit flow**: wizard captures forfeiture date, payment is posted and reconciled against deposit invoice
- **Unhold + return flow**: payment reverts to `draft`, credit note is created and reconciled, then payment is `cancel`led (kept for audit — `approval_code` and `ref_2` preserved)
- Guard: HLD journal blocked on rental invoice (only deposit invoice allowed)
- Guard: normal `action_post` blocked on `is_deposit_hold=True` payments (only forfeit flow may post)
- Guard: CN creation skipped while `deposit_hold_state == 'hold'` (prevents premature reconciliation)

## Capabilities

### New Capabilities
- `deposit-hold-payment`: Core hold payment lifecycle — create, processing state, forfeit, unhold, cancel
- `deposit-hold-ui`: Deposit invoice UI — On Hold badge, Unhold button, Forfeit button, wizard
- `deposit-hold-journals`: Journal configuration — `for_hold` flag and routing guards
- `deposit-hold-reporting`: Cancelled hold payment records preserved for audit and reporting

### Modified Capabilities
- None (no existing specs overlap)

## Impact

- `account.journal` — new `for_hold` field
- `account.payment` — new `is_deposit_hold` field, new `processing` and `cancel` state handling
- `account.move` — new `deposit_hold_state` computed field, Unhold/Forfeit action methods, guard on `action_register_payment`
- `sale.order.line` — guard in `_create_deposit_credit_note` to skip CN when hold is active
- New wizard model for forfeiture date entry
- New report: ใบมัดจำ (Deposit Certificate) for HLD holds
