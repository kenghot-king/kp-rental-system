## Why

ggg_rental's stock integration currently creates stock moves only at pickup/return time via the `write()` override. No reservation happens when a rental SO is confirmed — the "Free to Use" quantity stays unchanged, allowing overbooking when multiple rental orders compete for the same stock.

## What Changes

- On SO confirmation, create a delivery picking (WH/Stock → Rental Location) so stock is **reserved** and Free to Use drops immediately
- On pickup via wizard, **validate the existing picking** instead of creating new stock moves — qty_delivered field is locked (no partial pickup allowed)
- On return via wizard, **create and validate a new return picking** (Rental Location → WH/Stock) — partial returns still allowed
- On SO cancellation after pickup, **auto-create a return move** to bring stock back from Rental Location to WH/Stock
- On SO cancellation before pickup, picking is cancelled and reservation released (standard sale_stock behavior)
- Remove direct stock move creation in `write()` override (`_move_qty`, `_return_qty`) — replaced by picking-based flow

## Capabilities

### New Capabilities
- `rental-stock-reservation`: Stock reservation on SO confirmation via delivery picking to Rental Location, with full-qty pickup validation and partial return support
- `rental-cancel-return`: Auto-return of rented stock (qty_delivered - qty_returned) when a rental SO is cancelled after pickup

### Modified Capabilities

## Impact

- **Models**: `sale.order.line` — rework `_action_launch_stock_rule()`, `_create_procurements()`, `write()` override; remove or refactor `_move_qty`, `_return_qty`, `_move_serials`, `_return_serials`
- **Models**: `sale.order` — override cancel to handle auto-return
- **Wizard**: `rental.order.wizard.line` — make `qty_delivered` readonly on pickup
- **Views**: Wizard view update for readonly pickup qty
- **Dependencies**: No new dependencies (sale_stock already required)
