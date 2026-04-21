## Why

The product CSV import template (`/ggg_rental/download_product_template`) was built before `deposit_price`, `sale_ok`, and `taxes_id` were added to rental products. Staff downloading the template today cannot set these fields via import, forcing manual edits on every product after bulk upload.

## What Changes

- Add `deposit_price` (Float) column to the product CSV template and import handler
- Add `sale_ok` (Boolean) column to the product CSV template and import handler
- Add `taxes_id` (Many2many) column to the product CSV template and import handler — represented as semicolon-separated tax names; resolved by name against `account.tax` on import
- Update the example row in `download_product_template` to include values for all three new fields

## Capabilities

### New Capabilities

- `csv-product-fields`: CSV template and import support for `deposit_price`, `sale_ok`, and `taxes_id` fields on rental products

### Modified Capabilities

## Impact

- `addons/ggg_rental/controllers/rental_csv.py` — `PRODUCT_FIELDS`, example row, `_prepare_product_vals()`
- No model changes, no view changes, no migration needed
