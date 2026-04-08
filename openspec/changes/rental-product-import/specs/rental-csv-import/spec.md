## ADDED Requirements

### Requirement: Import products from CSV via custom controller
The system SHALL provide a `POST /ggg_rental/import_products` endpoint that accepts a CSV file upload and creates or updates rental products with pricing.

#### Scenario: Import new product with pricing
- **WHEN** CSV contains a row with `sap_article_code` = "SAP-001" that does not exist in the system
- **AND** the row includes `name`, `type`, `list_price`, and pricing columns "1 Day" = 1000, "1 Week" = 5000
- **THEN** the system SHALL create a new `product.template` with `rent_ok` = True
- **AND** create `product.pricing` records: 1 Day = 1000, 1 Week = 5000

#### Scenario: Update existing product fields
- **WHEN** CSV contains a row with `sap_article_code` = "SAP-001" that already exists
- **AND** the row has `name` = "Updated Name", `list_price` = 2000
- **THEN** the system SHALL overwrite the product's `name` and `list_price` with the CSV values

### Requirement: Merge pricing on update
The system SHALL use merge semantics when updating pricing for existing products.

#### Scenario: Pricing column with value updates or creates pricing
- **WHEN** existing product has pricing: 1 Hour = 200, 1 Day = 1000
- **AND** CSV row has columns "1 Day" = 1500, "1 Week" = 5000
- **THEN** 1 Hour pricing SHALL remain 200 (column not in CSV)
- **AND** 1 Day pricing SHALL be updated to 1500
- **AND** 1 Week pricing SHALL be created with value 5000

#### Scenario: Empty pricing cell deletes pricing
- **WHEN** existing product has pricing: 1 Day = 1000, 1 Week = 5000
- **AND** CSV row has column "1 Week" with empty value
- **THEN** 1 Week pricing SHALL be deleted
- **AND** 1 Day pricing SHALL remain unchanged (column not in CSV)

#### Scenario: Missing pricing column preserves existing pricing
- **WHEN** existing product has pricing: 1 Hour = 200, 1 Day = 1000, 1 Month = 15000
- **AND** CSV only has pricing columns "1 Day" and "1 Month"
- **THEN** 1 Hour pricing SHALL remain 200 (column absent from CSV entirely)

### Requirement: SAP article code is the match key
The system SHALL use `sap_article_code` to determine whether to create or update a product.

#### Scenario: Match by SAP article code
- **WHEN** CSV row has `sap_article_code` = "SAP-001"
- **AND** a product with `sap_article_code` = "SAP-001" exists in the database
- **THEN** the system SHALL update that existing product (not create a new one)

#### Scenario: New SAP article code creates product
- **WHEN** CSV row has `sap_article_code` = "SAP-NEW"
- **AND** no product with that code exists
- **THEN** the system SHALL create a new product with `rent_ok` = True

### Requirement: Import result reporting
The system SHALL return a JSON result after import with counts and warnings.

#### Scenario: Successful import with mixed create and update
- **WHEN** CSV contains 5 new products and 3 existing products
- **THEN** the response SHALL include `{"created": 5, "updated": 3, "errors": 0, "warnings": []}`

#### Scenario: Unrecognized pricing column warning
- **WHEN** CSV contains a column "6 Months" that does not match any `sale.temporal.recurrence` record
- **AND** it is not a known product field
- **THEN** the response SHALL include a warning: "Unknown column '6 Months' — skipped"
- **AND** the import SHALL continue processing other columns

#### Scenario: Missing required field error
- **WHEN** a CSV row is missing `sap_article_code`
- **THEN** that row SHALL be skipped with an error reported in the response
- **AND** other valid rows SHALL still be processed

### Requirement: Import button on rental product view
The system SHALL provide an "Import Products" button on the rental product tree view that opens a file upload dialog.

#### Scenario: Import button triggers file upload
- **WHEN** user clicks "Import Products" on the rental product list
- **THEN** a dialog SHALL appear allowing the user to select a CSV file
- **AND** after upload, the system SHALL display the import result (created, updated, errors, warnings)

#### Scenario: Import button only visible on rental view
- **WHEN** user is on the general product list view (not rental)
- **THEN** the "Import Products" button SHALL NOT be visible
