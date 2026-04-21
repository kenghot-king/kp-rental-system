## 1. Model — Computed Fields

- [x] 1.1 Add `rental_completion` stored Selection field (`complete`/`incomplete`) on `sale.order` with `@api.depends('order_line.qty_delivered', 'order_line.qty_returned', 'order_line.is_rental')` and `_compute_rental_completion` method
- [x] 1.2 Add `rental_completion_detail` non-stored Char field on `sale.order` computed alongside `rental_completion`
- [x] 1.3 Implement `_compute_rental_completion` logic: check returned axis (sum qty_returned vs sum qty_delivered), paid axis (posted out_invoices excluding deposit, payment_state), deposit refund axis (sum credit note amounts vs deposit invoice amounts), build detail text
- [x] 1.4 Add helper method `_get_deposit_invoices()` on `sale.order` to identify posted out_invoices with `is_rental_deposit` product lines

## 2. Recompute Triggers

- [x] 2.1 Add explicit recompute call in `sale.order.line._create_deposit_credit_note()` after credit note creation
- [x] 2.2 Override `account.move.write()` to trigger `rental_completion` recompute on linked sale orders when `payment_state` changes on posted out_invoices

## 3. Views

- [x] 3.1 Add completion badge to Form view (`sale_order_views.xml`) with tooltip via `title` attribute, hidden when not rental or not confirmed
- [x] 3.2 Add completion badge column to List view with tooltip, positioned after `rental_status`
- [x] 3.3 Add completion badge to Kanban view template with `t-att-title` for tooltip
- [x] 3.4 Add search filter for completion status in the rental order search view

## 4. Verification

- [x] 4.1 Test complete scenario: all returned + all paid + deposits fully refunded → status shows "Complete"
- [x] 4.2 Test incomplete scenario: partial return → tooltip shows correct returned ratio
- [x] 4.3 Test incomplete scenario: unpaid invoice → tooltip shows correct paid ratio
- [x] 4.4 Test incomplete scenario: partial deposit refund → tooltip shows correct amounts
- [x] 4.5 Test no-deposit scenario: order without deposits → deposit line omitted from tooltip, completion only checks returned + paid
- [x] 4.6 Test search/filter by completion status works correctly
