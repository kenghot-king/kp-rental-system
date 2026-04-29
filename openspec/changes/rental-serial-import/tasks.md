## 1. Serial Template Download

- [x] 1.1 Add `SERIAL_FIELDS = ['sap_article_code', 'serial_number']` constant to `controllers/rental_csv.py`
- [x] 1.2 Implement `GET /ggg_rental/download_serial_template` endpoint — returns CSV with header row + one example row
- [x] 1.3 Set `Content-Disposition` to `rental_serial_template.csv`

## 2. Serial Import Controller

- [x] 2.1 Implement `POST /ggg_rental/import_serials` endpoint — accepts CSV file upload via multipart/form-data
- [x] 2.2 Resolve target location: active company's default warehouse `lot_stock_id`; abort with config error if missing
- [x] 2.3 Implement CSV parsing: validate header has both `sap_article_code` and `serial_number`; trim whitespace
- [x] 2.4 Implement per-row validation (state machine): sap_code lookup → rent_ok → is_storable → tracking==serial → single variant
- [x] 2.5 Implement duplicate detection: search `stock.lot` for `(product_id, name)`; treat in-CSV duplicates the same as pre-existing
- [x] 2.6 Implement creation: `stock.lot.create({product_id, name, company_id})`, then `stock.quant` with `inventory_quantity=1.0` and `_apply_inventory()`
- [x] 2.7 Wrap each row in a savepoint so a single failure does not abort the whole import
- [x] 2.8 Return JSON: `{created, skipped, errors, warnings[], row_errors[]}`

## 3. Import UI

- [x] 3.1 Add "Download Serial Template" button to rental product tree view header (next to existing "Download Product Template")
- [x] 3.2 Add "Import Serials" button to rental product tree view header (next to existing "Import Products")
- [x] 3.3 Reuse the existing JS upload dialog pattern; route to `/ggg_rental/import_serials`
- [x] 3.4 Display result dialog showing created / skipped / errors counts plus warnings and row_errors lists

## 4. Configuration Guide Update

- [x] 4.1 Add new section to `documents/configuration/initial_config.md` titled "Before importing serials" placed after § 6 Rental Products Setup
- [x] 4.2 Document the standard_price prerequisite (set cost on every product before import; explain consequences of zero-cost imports)
- [x] 4.3 Document the one-time accountant journal entry to retire the prior fleet asset row, with example debit/credit lines
- [x] 4.4 Update the post-install verification checklist (§ 10) with a "Standard price set on all rental products" item

## 5. Integration & Testing

- [x] 5.1 Test happy path: download template → add 5 serials for a serial-tracked product → import → verify 5 lots created and 5 quants at WH/Stock with qty 1.0 each
- [x] 5.2 Test re-import: run the same CSV again → verify all 5 rows reported as `skipped` with warnings, no duplicates created
- [x] 5.3 Test in-CSV duplicates: upload a CSV with the same serial twice for the same product → verify first creates, second skips with warning
- [x] 5.4 Test validation errors: rows with missing sap_code, non-rentable product, non-serial-tracked product, multi-variant template — verify each lands in `row_errors` with a clear message and other rows still process
- [x] 5.5 Test missing warehouse config: temporarily clear `lot_stock_id` → verify import aborts with a clear error before processing rows
- [x] 5.6 Test accounting: verify journal entries are created with debit to Stock Valuation and credit to Inventory Adjustment at `product.standard_price`
- [x] 5.7 Test zero-cost product: import a product with `standard_price = 0` → verify lot/quant created but no valuation entry (or zero-value entry per Odoo behavior)
