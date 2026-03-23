## 1. Procurement & Picking on SO Confirmation

- [x] 1.1 Override `_get_location_final()` on `sale.order.line` — return `company.rental_loc_id` for rental lines (simpler than overriding `_create_procurements`)
- [x] 1.2 Update `_action_launch_stock_rule()` — remove the rental line skip so rental lines go through normal stock rule flow
- [x] 1.3 Verify: confirming a rental SO creates a delivery picking (WH/Stock → Rental Location) in "assigned" state with stock reserved

## 2. Pickup — Validate Existing Picking

- [x] 2.1 Implement `_validate_rental_pickup()` on `sale.order.line` — find the delivery picking for this SOL and validate it (set quantity, picked=True, _action_done)
- [x] 2.2 For serial-tracked products: assign selected `lot_ids` to the picking's move lines before validation
- [x] 2.3 Update `write()` override — on `qty_delivered` change for rental lines, call `_validate_rental_pickup()` instead of `_move_qty()` / `_move_serials()`
- [x] 2.4 Remove `_move_qty()` method (replaced by picking validation)
- [x] 2.5 Remove `_move_serials()` method (replaced by picking validation with lot assignment)

## 3. Return — Create New Picking

- [x] 3.1 Implement `_create_rental_return(qty, lot_ids=None)` on `sale.order.line` — create a new return picking (Rental Location → WH/Stock), assign lots if serial-tracked, validate immediately
- [x] 3.2 Update `write()` override — on `qty_returned` change for rental lines, call `_create_rental_return()` instead of `_return_qty()` / `_return_serials()`
- [x] 3.3 Remove `_return_qty()` method (replaced by return picking creation)
- [x] 3.4 Remove `_return_serials()` method (replaced by return picking creation)

## 4. Wizard — Lock Pickup Quantity

- [x] 4.1 Make `qty_delivered` field readonly in wizard view (always readonly, force_save="1")
- [x] 4.2 Ensure wizard sets `qty_delivered` to full reserved qty on pickup (verified: default behavior correct)

## 5. Cancel — Auto-Return

- [x] 5.1 Override `sale.order._action_cancel()` — for rental lines with `qty_delivered - qty_returned > 0`, call `_create_rental_return()` for the outstanding quantity
- [x] 5.2 For serial-tracked products: pass `pickedup_lot_ids - returned_lot_ids` as lot_ids to the return
- [x] 5.3 Let standard `sale_stock` cancellation handle the case where no pickup occurred (cancels picking, releases reservation)

## 6. Bug Fixes & Improvements

- [x] 6.1 Fix `stock.move` creation — remove invalid `name` field (Odoo 19 uses computed `reference` field)
- [x] 6.2 Fix wizard `_apply()` — change `order_line.update(vals)` to `order_line.write(vals)` for atomic field updates (prevents `returned_lot_ids` being empty when `qty_returned` triggers stock move)
- [x] 6.3 Add pickup quantity constraint — prevent selecting more serials than `product_uom_qty` on the SO line
- [x] 6.4 Fix pickup serial list — show all available serials in stock (not just reserved ones), pre-select reserved lot, exclude serials currently rented out

## 7. Verification

- [x] 7.1 Test: Confirm rental SO → delivery picking created, Free to Use drops, On Hand unchanged
- [x] 7.2 Test: Pickup via wizard → delivery picking validated, On Hand drops
- [x] 7.3 Test: Return via wizard → return picking created and validated, On Hand increases
- [x] 7.4 Test: Partial return creates proportional return picking
- [x] 7.5 Test: Service-type rental products do not create pickings
- [x] 7.6 Test: Non-rental lines on same SO still create normal customer delivery pickings
- [x] 7.7 Test: Serial-tracked pickup assigns correct lots to picking move lines
- [x] 7.8 Test: Serial-tracked return creates return picking with correct lots
- [x] 7.9 Test: Cancel SO before pickup → picking cancelled, reservation released
- [x] 7.10 Test: Cancel SO after pickup → auto-return picking created, On Hand restored
- [x] 7.11 Test: Cancel SO after partial return → auto-return for outstanding qty only
