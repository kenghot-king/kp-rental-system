## 1. Extend `_create_rental_return()` to accept a picking

- [x] 1.1 Add `picking=None` parameter to `_create_rental_return()` in `models/sale_order_line.py`
- [x] 1.2 When `picking` is provided: set `picking_id=picking.id` and `origin=order.name` on the `stock.move`, skip `_action_confirm` / `_action_assign` / `_action_done` (picking handles validation)
- [x] 1.3 When `picking` is None: keep existing behavior (standalone move, immediate validate) for backward compatibility — add `_logger.warning(...)` so the gap is visible in logs

## 2. Orchestrate pickings in the return wizard

- [x] 2.1 In `RentalOrderWizardLine._apply()` in `wizard/rental_processing.py`, add a pre-pass before line processing: for each return wizard line determine `location_dest_id`, create one `stock.picking` per unique destination and store in a local `picking_map = {dest_loc_id: picking}` dict
- [x] 2.2 Each picking created in the pre-pass: `picking_type_id = warehouse.in_type_id`, `origin = order.name`, `location_id = company.rental_loc_id`, `location_dest_id = dest`, `partner_id = order.partner_id`
- [x] 2.3 Pass the picking to `_create_rental_return()` by storing `picking_map` in the write context via `rental_return_picking_map = {dest_loc_id: picking.id}` so the `sale_order_line.write()` override can look it up and forward it
- [x] 2.4 In `sale_order_line.write()` override, read `rental_return_picking_map` from context; look up picking by `rental_return_dest_id`; pass it to `_create_rental_return(picking=...)`
- [x] 2.5 Add a post-pass in `_apply()` after all lines are processed: for each picking in `picking_map`, assign quantities and call `picking._action_done()`
