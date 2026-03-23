## 1. Dependencies & Configuration

- [x] 1.1 Add `sale_stock` to ggg_rental `__manifest__.py` depends list
- [x] 1.2 Extend `res.company` with `rental_loc_id` field (Many2one to stock.location, domain=[('usage','=','internal')])
- [x] 1.3 Create `_create_rental_location()` method on res.company — creates "Rental" internal location under Customers location for each company missing one
- [x] 1.4 Override `_create_per_company_locations()` to auto-create rental location for new companies
- [x] 1.5 Add post_init_hook to create rental locations for existing companies on module install

## 2. Stock Move Logic on Sale Order Line

- [x] 2.1 Override `sale.order.line.write()` — detect changes to `qty_delivered`/`qty_returned` on rental lines with storable products, call stock move methods
- [x] 2.2 Implement `_move_qty(qty, location_id, location_dest_id)` — create and immediately validate a stock move for the given quantity between locations
- [x] 2.3 Implement `_return_qty(qty, location_id, location_dest_id)` — reverse a previous stock move by reducing move line quantities
- [x] 2.4 Override `_action_launch_stock_rule()` — skip rental lines (prevent normal delivery picking creation on SO confirmation)
- [x] 2.5 Ensure `qty_delivered_method = 'manual'` for rental lines (already exists, verify it stays correct with sale_stock installed)

## 3. Views & Data

- [x] 3.1 Add `rental_loc_id` field to res.company form view (or res.config.settings)
- [x] 3.2 Create data XML for post_init_hook or add to existing rental_data.xml if needed
- [x] 3.3 Add rental stock moves smart button to sale order form view

## 4. Serial Number Tracking

- [x] 4.1 Add `pickedup_lot_ids`, `returned_lot_ids` fields on sale.order.line
- [x] 4.2 Implement `_move_serials()` — move specific serial numbers between locations
- [x] 4.3 Implement `_return_serials()` — undo serial number moves
- [x] 4.4 Update `write()` to branch on `product_id.tracking == 'serial'` vs quantity-based
- [x] 4.5 Extend wizard with `pickeable_lot_ids`, `returnable_lot_ids`, `pickedup_lot_ids`, `returned_lot_ids`
- [x] 4.6 Add onchange methods to sync qty from serial count
- [x] 4.7 Update wizard view with Serial Numbers column (many2many_tags)
- [x] 4.8 Update `_apply()` to pass lot_ids to SOL alongside qty changes

## 5. Verification

- [ ] 5.1 Test: Confirm rental SO → no delivery picking created for rental lines
- [ ] 5.2 Test: Pickup via wizard → stock moves out of warehouse into rental location, On Hand decreases
- [ ] 5.3 Test: Return via wizard → stock moves back from rental location to warehouse, On Hand increases
- [ ] 5.4 Test: Partial pickup/return creates proportional stock moves
- [ ] 5.5 Test: Service-type rental products do not create stock moves
- [ ] 5.6 Test: Non-rental lines on same SO still create normal delivery pickings
- [ ] 5.7 Test: Serial-tracked product pickup shows available S/N tags, qty auto-calculated
- [ ] 5.8 Test: Serial-tracked product return shows only picked-up S/N, moves back to warehouse
