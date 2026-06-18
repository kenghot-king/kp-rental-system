## Why

The system currently displays a red availability indicator and a negative "Forecasted Stock" tooltip when a rental line exceeds available inventory, but does not prevent the user from saving or confirming an overbooked order. This silently allows operators to commit to rentals the warehouse cannot fulfill, causing customer-facing failures at pickup time. A hard block at save and confirm — with a clear error message naming the gap — eliminates this category of error entirely.

## What Changes

- Add an action method `action_check_rental_availability()` on `sale.order` that validates every rental line on the order against the product's currently available quantity at the warehouse, raising a helpful `ValidationError` if any line is overbooked.
- Override `_action_confirm()` to call the new action method before the order transitions from `draft` to `sale`, so confirmation is hard-blocked when stock is insufficient.
- Add a live `onchange` warning on `sale.order.line` that surfaces the same gap as soon as the user edits product or quantity on a line, before they ever click confirm.
- Skip the validation entirely for service products (no inventory to check).
- Sum quantities across all lines for the same product within a single order before comparing — multi-line same-product orders cannot bypass the check by splitting.
- Drafts and quotations remain freely editable; the check fires only at confirmation. This matches the existing `action_sync_deposits` pattern, where work happens explicitly at meaningful moments rather than on every save.
- Produce a helpful error message that names the product, requested quantity, currently available quantity, and a corrective action hint.

## Capabilities

### New Capabilities
- `rental-availability-enforcement`: Hard validation that prevents rental sale orders from committing to quantities the warehouse cannot supply, with both live (onchange) and authoritative (constraint) enforcement layers.

### Modified Capabilities
<!-- None — purely additive. -->

## Impact

- **Models:**
  - `addons/ggg_rental/models/sale_order.py` gains an `action_check_rental_availability()` method and an override of `_action_confirm()`.
  - `addons/ggg_rental/models/sale_order_line.py` gains an `@api.onchange` warning hook on `product_id` / `product_uom_qty`.
- **Behavior:** Operators attempting to confirm an overbooked order see a friendly, actionable error. Drafts and quotations save without restriction — the block happens at confirm, where it matters. Existing already-confirmed orders are unaffected (the check runs only at the draft→sale transition).
- **Performance:** The check runs once at confirmation per order (one `free_qty` lookup per distinct product on the order). Onchange runs per-line on edit. Both are negligible at single-order scale.
- **No DB schema change.** No new fields, no migration. Pure logic.
- **No breaking changes** for orders within stock; legacy overbooked already-confirmed orders are not re-validated.
