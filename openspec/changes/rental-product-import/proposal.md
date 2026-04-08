## Why

Setting up rental products requires manually entering product details and multiple pricing rules one by one through the UI. For businesses with large product catalogs (e.g., equipment rental with SAP-managed inventory), this is impractical. Users need a way to bulk-import rental products with their pricing from CSV files, using their existing SAP article codes as stable reference keys.

## What Changes

- Add `sap_article_code` field to `product.template` (required, unique, indexed) as a business key for product identification across systems
- Add "Download Template" buttons on the rental product list view that generate dynamic CSV templates reflecting current system configuration (categories, UoMs, recurrence periods)
- Add a custom import controller that processes a single CSV file containing both product data and rental pricing (pricing periods as dynamic columns)
- Import logic uses `sap_article_code` as the match key: existing products are updated, new codes create new products
- Product fields are fully overwritten on update; pricing uses merge semantics (only columns present in CSV are touched, empty cell = delete that pricing rule, missing column = keep existing)

## Capabilities

### New Capabilities
- `sap-article-code`: New required unique field on product.template for cross-system product identification
- `rental-csv-template`: Dynamic CSV template download for rental products with pricing period columns generated from sale.temporal.recurrence
- `rental-csv-import`: Custom CSV import controller for rental products with single-file product + pricing import, merge-based pricing updates, and sap_article_code matching

### Modified Capabilities

(none)

## Impact

- **Models**: `product.template` — new `sap_article_code` field (DB migration needed on existing products)
- **Views**: Rental product tree/form views — new field + download/import buttons
- **Controllers**: New `/ggg_rental/download_template` and `/ggg_rental/import_products` endpoints
- **Dependencies**: No new external dependencies (uses standard `csv` module)
- **Existing data**: Existing products will need `sap_article_code` populated (migration or manual entry)
