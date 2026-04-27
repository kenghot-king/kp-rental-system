## 1. Helper for availability message

- [x] 1.1 Add a private method `_get_availability_error_message(product, requested_qty, available_qty, warehouse)` on `sale.order.line` that returns the localized message used by both the confirm-time check and the onchange warning

## 2. Order-level availability check method

- [x] 2.1 Add public method `action_check_rental_availability()` on `sale.order` in `addons/ggg_rental/models/sale_order.py` (next to `action_sync_deposits`)
- [x] 2.2 Group rental lines by product within the order, sum `product_uom_qty`, skip service products
- [x] 2.3 For each product group, fetch `free_qty` with the order's warehouse in context
- [x] 2.4 Use `float_compare` with the product's UOM rounding to compare requested total vs available
- [x] 2.5 Raise `ValidationError` (using the shared helpful-message helper) on the first overbooked product encountered
- [x] 2.6 Return `True` if all lines pass

## 3. Enforce at confirm

- [x] 3.1 Override `_action_confirm()` on `sale.order` to call `action_check_rental_availability()` before `super()._action_confirm()` — only for rental orders (`is_rental_order`)

## 4. Live onchange warning

- [x] 4.1 Add `@api.onchange('product_id', 'product_uom_qty')` method `_onchange_check_rental_availability` on `sale.order.line`
- [x] 4.2 Skip non-rental lines and service products
- [x] 4.3 If `product_uom_qty > free_qty` for the line's product (per-line, not summed), return `{'warning': {'title': ..., 'message': ...}}` using the shared message helper

## 5. Manual verification

- [x] 5.1 Create a draft rental order with Product X qty 5 where `free_qty = 2`, save → save succeeds (drafts free)
- [x] 5.2 Editing the same line, observe the onchange warning dialog appears with product name, qty, available, warehouse
- [x] 5.3 Click Confirm → confirmation blocked with helpful error message; order remains draft
- [x] 5.4 Reduce qty to 2, save and confirm → confirmation succeeds; order moves to `sale`
- [x] 5.5 Add a second line for the same product with qty 1; confirm → blocked (sum 3 > 2)
- [x] 5.6 Switch one line's product to a service product; confirm → succeeds for that line regardless of qty

## 6. Regression checks

- [x] 6.1 Confirm a non-rental sale order with qty exceeding stock — succeeds (no rental check fires)
- [x] 6.2 Confirm an in-stock rental order — succeeds normally, no spurious errors
- [x] 6.3 Cancel a rental order; the cancelled qty is no longer counted by `free_qty` (handled by Odoo stock module — verify by cancelling and observing `free_qty` increase)
