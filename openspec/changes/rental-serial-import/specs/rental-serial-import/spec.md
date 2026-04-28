## ADDED Requirements

### Requirement: Download serial number CSV template

The system SHALL provide a `GET /ggg_rental/download_serial_template` endpoint that returns a CSV file with the headers `sap_article_code` and `serial_number` plus one example row.

#### Scenario: User downloads the serial template

- **WHEN** an authenticated user requests `GET /ggg_rental/download_serial_template`
- **THEN** the response SHALL be a CSV file with `Content-Disposition` header set to `rental_serial_template.csv`
- **AND** the first row SHALL contain exactly the headers `sap_article_code,serial_number`
- **AND** at least one example data row SHALL be present

### Requirement: Import serials from CSV via custom controller

The system SHALL provide a `POST /ggg_rental/import_serials` endpoint that accepts a CSV file upload, creates `stock.lot` records for serial-tracked rental products, and lands each serial at the active company's default warehouse `lot_stock_id` with quantity 1.0 via the inventory adjustment mechanism.

#### Scenario: Import a new serial number

- **WHEN** the CSV contains a row with `sap_article_code` = "FORK-001" and `serial_number` = "SN-2026-001"
- **AND** a `product.template` exists with `sap_article_code` = "FORK-001", `rent_ok` = True, `is_storable` = True, `tracking` = 'serial', and exactly one variant
- **AND** no `stock.lot` exists for that product with name "SN-2026-001"
- **THEN** the system SHALL create a `stock.lot` with `product_id` set to that product's variant, `name` = "SN-2026-001", and `company_id` set to the active company
- **AND** create a `stock.quant` for that lot at the active company's default warehouse `lot_stock_id` with quantity 1.0 via `_apply_inventory()`

#### Scenario: All serials land at the default warehouse stock location

- **WHEN** the CSV is processed
- **THEN** every created serial SHALL be placed at the active company's default warehouse `lot_stock_id` (WH/Stock)
- **AND** no row SHALL allow specifying an alternate destination location

### Requirement: Warn and skip duplicate serials

The system SHALL NOT create a duplicate `stock.lot` for the same `(product_id, serial_number)` pair. Duplicates — whether already in the database or duplicated within the same upload — SHALL be skipped with a warning.

#### Scenario: Serial already exists in the database

- **WHEN** the CSV row references `sap_article_code` = "FORK-001" and `serial_number` = "SN-2026-001"
- **AND** a `stock.lot` already exists with `product_id` matching that product and `name` = "SN-2026-001"
- **THEN** the row SHALL be skipped (no new lot or quant created)
- **AND** the response SHALL include a warning identifying the row, the SAP code, and the serial number
- **AND** the response `skipped` count SHALL be incremented

#### Scenario: Same serial appears twice in the same upload

- **WHEN** two rows in the same CSV both have `sap_article_code` = "FORK-001" and `serial_number` = "SN-2026-001"
- **THEN** the first row SHALL create the lot
- **AND** the second row SHALL be skipped with a warning identifying it as a duplicate within the upload

### Requirement: Validate per row before creating

The system SHALL validate each row independently and SHALL skip invalid rows with an error in the response without aborting the import. Rows that pass all validations SHALL be processed normally.

#### Scenario: SAP code not found

- **WHEN** a row has `sap_article_code` = "FORK-999" and no `product.template` exists with that code
- **THEN** the row SHALL be added to `row_errors` with a message naming the unknown code
- **AND** the row SHALL NOT create any lot or quant
- **AND** subsequent rows SHALL still be processed

#### Scenario: Product is not rentable

- **WHEN** the matched product has `rent_ok` = False
- **THEN** the row SHALL be added to `row_errors` with a message indicating the product is not a rental product

#### Scenario: Product is not storable

- **WHEN** the matched product has `is_storable` = False (service or pure consumable)
- **THEN** the row SHALL be added to `row_errors` with a message indicating the product is not storable

#### Scenario: Product is not serial-tracked

- **WHEN** the matched product has `tracking` not equal to 'serial'
- **THEN** the row SHALL be added to `row_errors` with a message indicating the product is not serial-tracked

#### Scenario: Product template has multiple variants

- **WHEN** the matched `product.template` has more than one `product.product` variant
- **THEN** the row SHALL be added to `row_errors` with a message indicating the variant is ambiguous and the serial cannot be assigned

#### Scenario: Missing serial number

- **WHEN** a row has an empty `serial_number` cell
- **THEN** the row SHALL be added to `row_errors` and skipped

### Requirement: Default warehouse must be configured

The system SHALL abort the import with a configuration error before processing any row if the active company has no default warehouse or the default warehouse has no `lot_stock_id`.

#### Scenario: No warehouse configured

- **WHEN** the active company has no `stock.warehouse` record
- **THEN** the response SHALL be a configuration error message and HTTP status indicating failure
- **AND** no rows SHALL be processed

#### Scenario: Warehouse has no stock location

- **WHEN** the active company's default warehouse has `lot_stock_id` unset
- **THEN** the response SHALL be a configuration error naming the warehouse
- **AND** no rows SHALL be processed

### Requirement: Inventory adjustment posts at product standard price

The system SHALL use `stock.quant._apply_inventory()` to materialize the stock change so that journal entries are posted at each product's `standard_price` to the company's Stock Valuation account, with the Inventory Adjustment account as counterpart.

#### Scenario: Serial creation books to Stock Valuation

- **WHEN** a row creates a serial for a product with `standard_price` = 10000
- **THEN** the resulting accounting entry SHALL debit Stock Valuation by 10000
- **AND** credit the Inventory Adjustment account by 10000

#### Scenario: Zero-cost product creates lot without valuation impact

- **WHEN** a row creates a serial for a product with `standard_price` = 0
- **THEN** the lot and quant SHALL still be created
- **AND** the accounting entry SHALL be zero-valued (or absent, per Odoo's standard behavior for zero-cost moves)

### Requirement: JSON result reporting

The system SHALL return a JSON response after import with explicit counts and detail arrays.

#### Scenario: Mixed result with creates, skips, and errors

- **WHEN** the CSV contains 5 valid new serials, 2 already-existing serials, and 1 row with an unknown SAP code
- **THEN** the response SHALL include `created` = 5, `skipped` = 2, and `errors` = 1
- **AND** `warnings` SHALL contain entries for each skipped row
- **AND** `row_errors` SHALL contain an entry for the unknown SAP code naming the row number

#### Scenario: Row processing is independent

- **WHEN** any single row fails validation or raises an exception
- **THEN** the failure SHALL be recorded in `row_errors` and SHALL NOT prevent processing of other rows

### Requirement: Import UI buttons on rental product list

The system SHALL provide "Download Serial Template" and "Import Serials" buttons in the rental product tree view header, grouped with the existing rental product import buttons.

#### Scenario: Buttons visible only in the rental product view

- **WHEN** the user navigates to the rental product list view (context `in_rental_app`)
- **THEN** both "Download Serial Template" and "Import Serials" buttons SHALL be visible

#### Scenario: Buttons hidden in the general product view

- **WHEN** the user navigates to a non-rental product list view
- **THEN** neither button SHALL be visible

#### Scenario: Import button opens upload dialog

- **WHEN** the user clicks "Import Serials"
- **THEN** a file upload dialog SHALL appear allowing CSV selection
- **AND** after upload the system SHALL display a result dialog with the created, skipped, and errors counts plus the warnings and row_errors lists
