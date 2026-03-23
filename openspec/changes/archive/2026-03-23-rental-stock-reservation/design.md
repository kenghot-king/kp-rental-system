## Context

ggg_rental currently integrates with stock by creating and immediately validating stock moves inside `sale.order.line.write()` — when `qty_delivered` or `qty_returned` changes, `_move_qty()` / `_move_serials()` create a new `stock.move`, assign it, and mark it done in one step. The `_action_launch_stock_rule()` override skips rental lines entirely, so no picking or reservation happens on SO confirmation.

This means "Free to Use" never reflects pending rentals, leading to overbooking risk.

Enterprise's `sale_stock_renting` supports both modes (with/without pickings) via a feature flag. We're implementing the "with pickings" approach in a simplified form — delivery picking on confirm, no pre-created return picking.

## Goals / Non-Goals

**Goals:**
- Reserve stock on SO confirmation (Free to Use decreases)
- Full-quantity pickup only (validate existing delivery picking)
- Partial returns allowed (create new return picking)
- Auto-return stock on SO cancellation after pickup
- Support both serial-tracked and untracked products

**Non-Goals:**
- Partial pickup (explicitly disallowed)
- Pre-created return pickings on SO confirmation
- Rental-specific stock routes with automated rules
- Backorder handling (not needed since pickup is always full qty)

## Decisions

### 1. Override `_create_procurements()` to redirect rental lines to Rental Location

Standard `sale_stock` creates procurements to the Customer location. We override to set `location_dest_id = company.rental_loc_id` for rental lines, so the delivery picking goes WH/Stock → Rental Location.

**Why not a custom route?** Enterprise uses a dedicated `route_rental` with stock rules. That's more flexible but adds data records and configuration. Overriding `_create_procurements()` is simpler and sufficient for our single-mode approach.

### 2. Let `_action_launch_stock_rule()` run for rental lines (remove skip)

Currently rental lines are filtered out. We remove this filter so rental lines go through normal `sale_stock` flow — creating a delivery picking with reservation.

### 3. Validate existing picking on pickup instead of creating new moves

The `write()` override changes from calling `_move_qty()` / `_move_serials()` to finding the existing delivery picking's moves and validating them. Since pickup is always full quantity, we validate the entire picking — no backorders.

For serial-tracked products: assign the selected lot_ids to the move lines before validation.

### 4. Create new return picking on return

Returns create a fresh picking (Rental Location → WH/Stock) and validate it immediately. This is simpler than pre-creating return pickings and handles partial returns naturally — each return creates its own picking for the returned quantity.

### 5. Lock `qty_delivered` in wizard on pickup

The wizard's `qty_delivered` field becomes readonly when `status == 'pickup'`. The quantity is always the full reserved amount. Users can still select which serial numbers for tracked products.

### 6. Auto-return on SO cancellation

Override `sale.order._action_cancel()`. If `qty_delivered - qty_returned > 0`, create and validate a return move for the outstanding quantity (or serial numbers). If no pickup has happened, the picking cancellation and unreservation is handled by standard `sale_stock` behavior.

### 7. Remove `_move_qty`, `_return_qty` and refactor `_move_serials`, `_return_serials`

These methods created standalone moves. They're replaced by:
- Pickup: `_validate_rental_pickup()` — validates existing picking moves
- Return: `_create_rental_return()` — creates and validates a return picking

## Risks / Trade-offs

- **[Risk] Existing rental orders have moves without pickings** → Orders processed under the old flow have standalone stock moves, not part of any picking. The new flow expects pickings. Mitigation: old orders continue to work since `write()` only looks for pickings on new orders; document that existing in-progress rentals should be completed before upgrading.
- **[Risk] No partial pickup means inflexibility** → If a customer wants 2 of 3 items, they can't partially pick up. Mitigation: this is a deliberate simplification; can be revisited later.
- **[Trade-off] Return pickings not pre-created** → No visibility into expected returns in the picking list. Acceptable for now; the rental wizard and SO views still show return status.
