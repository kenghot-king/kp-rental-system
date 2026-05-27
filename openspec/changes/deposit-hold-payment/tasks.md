## 1. Data Model

- [x] 1.1 Add `for_hold` Boolean field to `account.journal` (default `False`, string "Hold Journal")
- [x] 1.2 Add `is_deposit_hold` Boolean field to `account.payment` (default `False`)
- [x] 1.3 Add `approval_code` Char field to `account.payment` (already existed — reused)
- [x] 1.4 Add `ref_2` Char field to `account.payment` (`payment_reference_2` already existed — reused; added `hold_state` and `deposit_invoice_id`)
- [x] 1.5 Add `processing` selection value to `account.payment.state` via `_inherit` (used `hold_state` field instead — Odoo 19 state is computed, `hold_state` tracks hold lifecycle cleanly)
- [x] 1.6 Add `deposit_hold_state` computed field on `account.move` (`'none'` / `'hold'`) — derived via `deposit_hold_payment_ids` One2many

## 2. Hold Payment Creation

- [x] 2.1 Override payment register `_create_payments` — when journal `for_hold=True` on a deposit invoice, create `account.payment` with `is_deposit_hold=True`, `hold_state='active'`, no journal entry (draft state)
- [x] 2.2 Guard in `_create_hold_payment`: raise `UserError` if journal `for_hold=True` and invoice is NOT a deposit invoice
- [x] 2.3 Override `account.payment.action_post` — raise `UserError` if `is_deposit_hold=True` and not called from forfeit flow (`_forfeit_flow=True` context)

## 3. Forfeit Flow

- [x] 3.1 Create `account.payment.forfeit.wizard` model with `date` field (default today), `payment_id` and `invoice_id` Many2one
- [x] 3.2 Create wizard form view with date field and Confirm button
- [x] 3.3 Add `action_forfeit` method on `account.move` — opens forfeit wizard
- [x] 3.4 Implement wizard `action_confirm`: update payment date, call `action_post` with `_forfeit_flow=True` context, reconcile payment with invoice

## 4. Unhold Flow

- [x] 4.1 Add `action_unhold` method on `account.move` — sets hold payment `hold_state='released'`, clears `deposit_hold_state`
- [x] 4.2 Guard in `sale.order.line._create_deposit_credit_note` — skip CN creation if `deposit_invoice.deposit_hold_state == 'hold'`
- [x] 4.3 After CN reconciliation, call `action_cancel()` and set `hold_state='cancelled'` on released hold payments (record kept)

## 5. UI

- [x] 5.1 Add "On Hold" ribbon badge on `account.move` form view, visible when `deposit_hold_state='hold'`
- [x] 5.2 Add Unhold button on `account.move` form, visible when `deposit_hold_state='hold'`, calls `action_unhold`
- [x] 5.3 Add Forfeit button on `account.move` form, visible when `deposit_hold_state='hold'`, opens forfeit wizard
- [x] 5.4 Add `for_hold` checkbox to `account.journal` form view
- [x] 5.5 Add `deposit_invoice_id` and `hold_state` fields to `account.payment` form view (visible when `is_deposit_hold=True`)

## 6. Deposit Certificate Report

- [x] 6.1 Create ใบมัดจำ (Deposit Certificate) QWeb report template — shows customer, hold amount, approval code, card reference, date, signatures
- [x] 6.2 Registered report action bound to `account.move` model

## 7. Reporting

- [x] 7.1 Add smart button on deposit invoice form to display related hold payment(s)
- [x] 7.2 Add `is_deposit_hold` filter to `account.payment` search panel (Credit Holds + Active Holds filters)
