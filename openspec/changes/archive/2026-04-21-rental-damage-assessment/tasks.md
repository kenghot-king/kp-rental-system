## 1. Damage Log Model & Company Settings

- [x] 1.1 Create `rental.damage.log` model with fields: lot_id, order_id, order_line_id, product_id, damage_fee, reason, date, user_id
- [x] 1.2 Add `damage_product` Many2one field to `res.company` (service product for damage fees)
- [x] 1.3 Add `damage_product` field to `res.config.settings` (related to company field)
- [x] 1.4 Add damage_product setting to the rental configuration view (`res_config_settings_views.xml`)

## 2. Stock Lot Extension

- [x] 2.1 Add `damage_log_ids` One2many and computed `damage_count` to `stock.lot`
- [x] 2.2 Add damage history smart button to `stock.lot` form view
- [x] 2.3 Create list and form views for `rental.damage.log` with search filters (product, lot, order, date)

## 3. Return Wizard — Condition Assessment Fields

- [x] 3.1 Add `condition` selection field (good/damaged, default good) to `rental.order.wizard.line`
- [x] 3.2 Add `damage_fee` float and `damage_reason` text fields to `rental.order.wizard.line`
- [x] 3.3 Update return wizard XML view: show condition column, conditionally show damage_fee and damage_reason when condition=damaged, hide all during pickup

## 4. Damage Fee Processing Logic

- [x] 4.1 Create `_generate_damage_line()` method on `sale.order.line` (similar to `_generate_delay_line`): find/create damage product, create SO line with fee and description
- [x] 4.2 Create `_prepare_damage_line_vals()` and `_get_damage_line_description()` helper methods on `sale.order.line`
- [x] 4.3 Update `_apply()` in `rental.order.wizard.line` to call `_generate_damage_line()` and create `rental.damage.log` records for damaged items, after late fee check and before qty_returned write

## 5. Module Registration

- [x] 5.1 Register `rental.damage.log` model in `models/__init__.py`
- [x] 5.2 Add new view XML files to `__manifest__.py` (damage log views, updated stock.lot views)
- [x] 5.3 Add security access rules for `rental.damage.log` in `ir.model.access.csv`
