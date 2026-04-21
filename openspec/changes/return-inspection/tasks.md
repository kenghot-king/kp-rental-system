## 1. Company Locations

- [x] 1.1 Add `damage_loc_id` and `inspection_loc_id` Many2one fields to `res.company` (domain: internal locations)
- [x] 1.2 Add `_create_rental_support_locations()` helper on `res.company` — creates "Damage" and "Inspection" internal locations for companies missing them
- [x] 1.3 Call `_create_rental_support_locations()` from `_create_per_company_locations()` so new companies get locations automatically
- [x] 1.4 Add `create_missing_rental_support_locations()` `@api.model` method for use in `post_init_hook`
- [x] 1.5 Register `post_init_hook` in `__manifest__.py` and implement it in `__init__.py` to call `create_missing_rental_support_locations()`

## 2. Settings

- [x] 2.1 Add `damage_loc_id` and `inspection_loc_id` related fields to `res.config.settings` (readonly=False, domain internal)
- [x] 2.2 Add both fields to the rental configuration section of the settings view (`views/res_config_settings_views.xml`)

## 3. Return Wizard — Model

- [x] 3.1 Add `('inspect', 'Inspect')` to the `condition` selection on `rental.order.wizard.line`
- [x] 3.2 In `_apply()`: resolve `location_dest_id` based on condition — good → `lot_stock_id`, damaged → `company.damage_loc_id`, inspect → `company.inspection_loc_id`
- [x] 3.3 In `_apply()`: raise `UserError` if condition = damaged and `damage_loc_id` not set, or condition = inspect and `inspection_loc_id` not set
- [x] 3.4 Pass resolved `location_dest_id` to `order_line._create_rental_return(qty, lot_ids, location_dest_id=...)` via context (`rental_return_dest_id`)
- [x] 3.5 Call `_process_damage()` for both `damaged` and `inspect` conditions (existing call already handles damaged; add inspect)

## 4. Stock Move — `sale_order_line.py`

- [x] 4.1 Add `location_dest_id=None` parameter to `_create_rental_return()`; default to `self.order_id.warehouse_id.lot_stock_id` when not provided
- [x] 4.2 Use the passed `location_dest_id` in the stock move creation and move line creation (both the main move and the serial-number move lines)

## 5. Return Wizard — View

- [x] 5.1 Update `rental_processing_views.xml`: change the `invisible` condition on damage fee and reason fields to show when `condition in ('damaged', 'inspect')` (currently only `damaged`)
