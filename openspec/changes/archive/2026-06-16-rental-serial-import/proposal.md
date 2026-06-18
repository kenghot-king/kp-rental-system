## Why

After product master data is imported (via the existing rental product CSV import), the next setup step is loading the physical fleet — every serial-tracked unit needs a `stock.lot` record and a `stock.quant` placing it at WH/Stock with quantity 1.0. For a fleet of hundreds of units, doing this through Odoo's standard inventory adjustment UI is tedious and error-prone, and the technical field names (`inventory_quantity`, `lot_id/name`) are not friendly to operations staff.

This change adds a dedicated CSV import for serial numbers that mirrors the existing rental product import pattern: download a template, fill in `sap_article_code` + `serial_number`, upload, and serials land at WH/Stock as bookable inventory with proper accounting.

## What Changes

- Add `GET /ggg_rental/download_serial_template` endpoint that returns a 2-column CSV (`sap_article_code`, `serial_number`) with one example row
- Add `POST /ggg_rental/import_serials` endpoint that parses the CSV, creates `stock.lot` records, and uses `_apply_inventory()` on `stock.quant` to land each serial at the active company's default warehouse `lot_stock_id` with `inventory_quantity = 1.0`
- Add "Download Serial Template" and "Import Serials" buttons to the rental product list view header, grouped with the existing product import buttons
- Validate per row: product must exist (by `sap_article_code`), be rentable, be storable, have `tracking='serial'`, and resolve to exactly one variant
- Warn-and-skip duplicate serials (already exist for the same product); errors and warnings reported in JSON response

## Capabilities

### New Capabilities
- `rental-serial-import`: Custom CSV import controller for serial numbers — creates stock.lot + stock.quant at WH/Stock for serial-tracked rental products, with sap_article_code as the product match key and per-product serial uniqueness

### Modified Capabilities

(none)

## Impact

- **Models**: None (no new fields; uses existing `stock.lot`, `stock.quant`, `product.template.sap_article_code`)
- **Views**: Rental product tree view — two new buttons in the header
- **Controllers**: New `/ggg_rental/download_serial_template` and `/ggg_rental/import_serials` endpoints in the existing `controllers/rental_csv.py`
- **Dependencies**: No new external dependencies (uses standard `csv` module and existing `stock` integration from `sale_stock`)
- **Configuration guide**: `documents/configuration/initial_config.md` gets a new "Before importing serials" section explaining that `standard_price` must be set on each product first, and that the accountant should record a one-time journal entry to retire the prior fleet asset row (since `_apply_inventory()` will book the fleet to Stock Valuation against the Inventory Adjustment account)
- **Existing data**: None affected; this is a setup-time tool
