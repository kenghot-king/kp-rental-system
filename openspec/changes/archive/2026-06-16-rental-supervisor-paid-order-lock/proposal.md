## Why

Once a rental order has a paid invoice, staff should not be able to accidentally edit rental items, deposit lines, or cancel the order — changes at that point affect accounting integrity. Only a Rental Supervisor should be able to override these restrictions, and even then, cancellation requires refunding all paid invoices first.

## What Changes

- Add computed field `has_paid_invoice` on `sale.order` — True when any posted `out_invoice` on the order has `payment_state` in `(paid, in_payment)`.
- Add computed field `can_edit_paid_order` on `sale.order` — True when the current user belongs to `ggg_rental.group_rental_supervisor`.
- Lock order line fields (`product_id`, `product_template_id`, `name`, `product_uom_qty`, `price_unit`, `discount`, `product_uom_id`, `tax_ids`) for lines where `is_rental` or `deposit_parent_id` is set, when `has_paid_invoice` is True and `can_edit_paid_order` is False.
- Late fine and damage charge lines (`is_rental=False`, `deposit_parent_id=False`) remain editable at all times.
- Deposit lines are editable when no paid invoice exists; locked only after first payment (unless supervisor).
- Block cancellation (`_action_cancel`) for rental orders with any paid invoice — applies to all users including supervisors. Supervisor must refund all paid invoices before cancelling.
- Hide the Cancel button at view level when `is_rental_order and has_paid_invoice`.

## Capabilities

### New Capabilities

- `rental-paid-order-lock`: Locks rental item and deposit lines from editing, and blocks cancellation, once any invoice on the rental order is paid. Rental Supervisors can edit paid orders; cancellation requires full refund for everyone.

### Modified Capabilities

## Impact

- `addons/ggg_rental/models/sale_order.py` — new computed fields, `_action_cancel` override
- `addons/ggg_rental/views/sale_order_views.xml` — readonly attributes on order line fields, cancel button visibility
- No schema changes, no new dependencies, no breaking changes for non-rental orders
