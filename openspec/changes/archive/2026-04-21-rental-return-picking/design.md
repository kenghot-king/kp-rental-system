## Context

Currently `_create_rental_return()` creates a standalone `stock.move`, calls `_action_confirm(merge=False)`, assigns quantities, and calls `_action_done()` — all without a `stock.picking`. The move has no `origin` and no `picking_id`.

The return wizard's `_apply()` iterates over `RentalOrderWizardLine` records. For each return line it:
1. Determines `location_dest_id` (Stock / Damage / Inspection based on `condition`)
2. Calls `order_line.write({'qty_returned': ...})` with `rental_return_dest_id` in context
3. The `write()` override in `sale_order_line.py` triggers `_create_rental_return()`

To group moves from the same return event by destination into shared pickings, the picking must be created **before** line processing and passed **into** `_create_rental_return()`.

## Goals / Non-Goals

**Goals:**
- Every rental return produces a `stock.picking` (WH/IN/xxxxx) visible in Inventory → Transfers
- `origin` on both the picking and each move is set to the sale order name
- Lines returning to the same destination in the same wizard submit share one picking
- Lines returning to different destinations get separate pickings
- Picking type is `Receipts` (`warehouse.in_type_id`) for all three destinations
- Backward compatibility: `_create_rental_return()` called without a picking works as before

**Non-Goals:**
- Changing the delivery (pickup) side — already creates proper pickings via Odoo standard flow
- Merging return pickings across multiple wizard submits
- Creating a dedicated "Rental Return" operation type

## Decisions

### Decision 1: Picking orchestration lives in the wizard, not in `_create_rental_return()`

`_create_rental_return()` is called deep inside `sale_order_line.write()`. Creating and validating pickings there cannot be grouped across lines. The wizard's `_apply()` is the correct place to orchestrate because it has visibility over all lines in the return event.

**Three-phase approach in `_apply()`:**

```
Phase 1 — Pre-pass (collect destinations, create pickings)
  for each wizard_line where status='return' and qty_returned > 0:
    determine location_dest_id
    if dest not in picking_map:
        create stock.picking(
            picking_type_id = warehouse.in_type_id,
            origin          = order.name,
            location_id     = company.rental_loc_id,
            location_dest_id = dest,
            partner_id      = order.partner_id,
        )
        picking_map[dest.id] = picking

Phase 2 — Main pass (process lines, create moves under pickings)
  for each wizard_line:
    apply qty changes (late fine, damage, stock move)
    _create_rental_return(..., picking=picking_map[dest.id])
      → creates stock.move(picking_id=picking.id, origin=order.name, ...)
      → does NOT call _action_done()

Phase 3 — Post-pass (validate all pickings)
  for picking in picking_map.values():
    picking._action_done()
```

### Decision 2: Pass picking via parameter, not context

`_create_rental_return(qty, lot_ids=None, location_dest_id=None, picking=None)`

Using a parameter is explicit and testable. Using context would be implicit and harder to reason about. The `write()` override calls `_create_rental_return()` — we pass the picking by adding it to `sale_order_line.write()`'s internal call after extracting it from context key `rental_return_picking`.

Concretely:
- Wizard sets `context['rental_return_picking_map'] = {dest_id: picking_id, ...}`
- `sale_order_line.write()` reads `rental_return_picking_map` from context and looks up the picking by `rental_return_dest_id`, then passes it to `_create_rental_return()`

### Decision 3: `origin` stamped on both picking and move

`stock.picking.origin = order.name` — appears in Transfers list "Source Document" column.
`stock.move.origin = order.name` — appears in Stock Moves History.

### Decision 4: `_action_done()` called on the picking, not on the move

When a move has a `picking_id`, validating via `picking._action_done()` is the correct Odoo pattern. Calling `move._action_done()` on a move that belongs to a picking bypasses picking-level logic (backorder handling, etc.).

## Risks / Trade-offs

- **Risk: `_action_done()` on picking triggers backorder dialog** → Mitigated by ensuring `quantity` and `picked` are set on all move lines before calling `_action_done()`. Odoo will not prompt for a backorder if all demand is fulfilled.
- **Risk: `rental_return_picking_map` context key not found** → `_create_rental_return()` falls back to standalone move (backward compat). Log a warning so the gap is detectable.
- **Trade-off: Multiple pickings per return event when destinations differ** → Intentional and correct. One clean picking per destination is better than one mixed picking.
- **Trade-off: WH/IN sequence used for internal returns (Damage/Inspect)** → The `Internal Transfers` type would be more semantically correct for Rental→Damage and Rental→Inspect (both internal locations). However, user decision is Receipts for all three for operational simplicity.

## Migration Plan

No database migration. Deploy by restarting Odoo service. Historical return moves without pickings are unaffected — they remain as-is.
