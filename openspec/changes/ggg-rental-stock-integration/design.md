## Context

ggg_rental currently manages rental quantities (`qty_delivered`, `qty_returned`) purely at the sale order line level with `qty_delivered_method = 'manual'`. No stock moves are created — the Inventory module's On Hand / Free to Use quantities are never affected by rental operations.

Enterprise solves this via a separate bridge module `sale_stock_renting` that depends on both `sale_renting` and `sale_stock`. It uses a **dedicated internal "Rental" location** per company — products move from warehouse stock to the rental location on pickup, and back on return. This keeps rented items in inventory valuation (they're still company assets) while showing them as unavailable for other uses.

Our ggg_rental depends on `['sale', 'ggg_gantt']`. The `sale` module in Odoo 19 CE does NOT include stock integration — that's provided by `sale_stock` (which is a CE module). We need to build the bridge between ggg_rental and sale_stock, equivalent to what `sale_stock_renting` does in Enterprise.

## Goals / Non-Goals

**Goals:**
- Rental pickup moves stock out of warehouse → rental location (internal)
- Rental return moves stock back from rental location → warehouse
- Partial pickup/return creates proportional stock moves
- Rented products stay in inventory valuation (internal location, not customer location)
- Stock availability reflects rental reservations (Free to Use decreases when rented out)
- Works for both tracked (serial/lot) and untracked products

**Non-Goals:**
- Serial number / lot tracking UI on the rental wizard (complex, defer to later)
- Rental-specific stock routes with automated pickings on SO confirmation (the "rental pickings" feature behind a feature flag in Enterprise — too complex for v1)
- Padding/preparation time affecting reservations
- Forecast availability during overlapping rental periods
- Stock valuation adjustments specific to rentals

## Decisions

### 1. Dedicated "Rental" internal location (same as Enterprise)

Products move: `Warehouse Stock → Rental Location` on pickup, `Rental Location → Warehouse Stock` on return.

**Why not Customer location?** Products sent to a Customer location leave inventory valuation. Rented products are still company assets — they should remain in internal locations. The Rental location is an internal child of the company's stock, just logically separate.

**Alternatives considered:**
- Customer location: simpler but wrong for accounting (assets disappear from books)
- Virtual location: doesn't affect physical inventory counts
- No location, just reserve quants: doesn't actually move stock

### 2. Stock moves created in SOL.write() override (same as Enterprise)

When `qty_delivered` or `qty_returned` changes on a rental SOL, the `write()` method creates immediate stock moves (confirmed + done). This hooks into the existing wizard flow without modifying the wizard itself.

**Why not modify the wizard?** The wizard calls `order_line.update({'qty_delivered': ...})` or `order_line.update({'qty_returned': ...})`. Overriding `write()` on the SOL catches all quantity changes regardless of source (wizard, manual edit, API).

### 3. Keep `qty_delivered_method = 'manual'` for rental lines

Enterprise keeps this as manual even with stock integration. The stock moves are created as a side effect, not as the source of truth for delivered quantities. This avoids conflicts with `sale_stock`'s normal flow which computes `qty_delivered` from stock moves.

### 4. Add `sale_stock` to ggg_rental dependencies

Rather than creating a separate bridge module (like Enterprise's `sale_stock_renting`), we integrate directly into `ggg_rental`. This is simpler for CE users who will always want stock integration with rentals.

**Trade-off:** ggg_rental now requires the stock module. This is acceptable because any real rental business needs inventory tracking.

## Risks / Trade-offs

- **[Risk] Existing rental orders have no stock moves** → On module upgrade, existing rented-out quantities won't be reflected in stock. Mitigation: post_init_hook or migration script to reconcile, or document as manual step.
- **[Risk] sale_stock's normal SO confirmation creates customer delivery pickings** → Rental lines should NOT create normal outgoing pickings. Mitigation: override `_action_launch_stock_rule()` to skip rental lines (they use manual stock moves instead).
- **[Risk] Concurrent write to qty_delivered from multiple sources** → Low risk since rental wizard is the primary path. Mitigation: stock moves are idempotent per write call.
- **[Trade-off] No serial number tracking in v1** → Simplifies implementation significantly. Can be added later.
