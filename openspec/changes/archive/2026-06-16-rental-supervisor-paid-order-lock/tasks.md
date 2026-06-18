## 1. Model — Computed Fields

- [ ] 1.1 Add `has_paid_invoice` non-stored computed field to `sale.order` — depends on `invoice_ids.state` and `invoice_ids.payment_state`; True when any `out_invoice` is `posted` with `payment_state in ('paid', 'in_payment')`
- [ ] 1.2 Add `can_edit_paid_order` non-stored computed field to `sale.order` — returns `self.env.user.has_group('ggg_rental.group_rental_supervisor')` with no record dependencies

## 2. Model — Cancel Guard

- [ ] 2.1 Override `_action_cancel` in `sale.order` to check `is_rental_order and has_paid_invoice`; raise `UserError` with message "Cannot cancel: please refund all paid invoices before cancelling." — applies to all users including supervisors

## 3. View — Invisible Fields

- [ ] 3.1 Add `has_paid_invoice` as an invisible field inside the `<header>` block of `rental_order_form_view` in `sale_order_views.xml`
- [ ] 3.2 Add `can_edit_paid_order` as an invisible field inside the `<header>` block

## 4. View — Cancel Button

- [ ] 4.1 Override the `action_cancel` button visibility in `rental_order_form_view` to add `or (is_rental_order and has_paid_invoice)` to its `invisible` condition

## 5. View — Order Line Field Readonly

- [ ] 5.1 Update xpath for `product_id` readonly attribute: replace `deposit_parent_id` with `(deposit_parent_id or is_rental) and parent.has_paid_invoice and not parent.can_edit_paid_order`
- [ ] 5.2 Update xpath for `product_template_id` readonly attribute with same combined condition
- [ ] 5.3 Update xpath for `name` readonly attribute with same combined condition
- [ ] 5.4 Update xpath for `product_uom_qty` readonly attribute with same combined condition
- [ ] 5.5 Update xpath for `price_unit` readonly attribute with same combined condition
- [ ] 5.6 Update xpath for `discount` readonly attribute with same combined condition
- [ ] 5.7 Update xpath for `product_uom_id` readonly attribute with same combined condition
- [ ] 5.8 Update xpath for `tax_ids` readonly attribute with same combined condition

## 6. Verification

- [ ] 6.1 Upgrade module (`-u ggg_rental`) and confirm no XML/Python errors
- [ ] 6.2 Test regular user: create rental order, pay invoice, confirm rental items and deposit lines are read-only, confirm late fine / damage lines are still editable
- [ ] 6.3 Test Rental Supervisor: same paid order, confirm all line fields are editable
- [ ] 6.4 Test cancel blocked: paid order, confirm Cancel button is hidden and `_action_cancel` raises error if triggered
- [ ] 6.5 Test cancel restored: after credit note + full refund, confirm Cancel button reappears and order can be cancelled
- [ ] 6.6 Test non-rental order: confirm cancel and line editing are unaffected
