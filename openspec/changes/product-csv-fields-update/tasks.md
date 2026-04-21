## 1. PRODUCT_FIELDS — Add new columns

- [x] 1.1 Add `sale_ok`, `deposit_price`, `taxes_id` to `PRODUCT_FIELDS` list in `rental_csv.py` (after `extra_daily`, before `uom_id` for `deposit_price`; `sale_ok` after `list_price`; `taxes_id` after `tracking`)

## 2. Download Template — Example row

- [x] 2.1 Add `sale_ok: 'True'` to the example row in `download_product_template()`
- [x] 2.2 Add `deposit_price: '5000.00'` to the example row
- [x] 2.3 Add `taxes_id` to the example row — query the first active sales tax by name and use it as the example value (fallback to `'Output 7% include'` if none found)

## 3. Import Handler — `_prepare_product_vals()`

- [x] 3.1 Add `sale_ok` handling — same bool pattern as `rent_ok` (`raw.lower() in ('true', '1', 'yes')`)
- [x] 3.2 Add `deposit_price` handling — same float pattern as `list_price`
- [x] 3.3 Add `taxes_id` handling — split by `;`, strip whitespace, search `account.tax` by name with `type_tax_use='sale'`, build `[(6, 0, [ids])]`; append a warning for each name that fails to resolve (return warnings via a mechanism — see note below)

## 4. Import Warnings — surface unresolved tax names

- [x] 4.1 Thread a `warnings` list into `_prepare_product_vals()` (add `warnings=None` parameter) so unresolved tax names can be appended and surfaced in the JSON response
