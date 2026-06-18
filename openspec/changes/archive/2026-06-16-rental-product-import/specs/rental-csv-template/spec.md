## ADDED Requirements

### Requirement: Download product CSV template
The system SHALL provide a button on the rental product tree view to download a dynamically generated CSV template for product import.

The template SHALL include:
- Fixed columns: `sap_article_code`, `name`, `type`, `categ_id`, `list_price`, `rent_ok`, `extra_hourly`, `extra_daily`, `uom_id`, `tracking`, `default_code`, `barcode`, `description_sale`
- Dynamic columns: one column per `sale.temporal.recurrence` record, using `duration_display` with `en_US` locale as header (e.g., "1 Hour", "1 Day", "1 Week")
- One example row with realistic sample values
- Column headers in English

#### Scenario: Download product template with current recurrences
- **WHEN** the system has recurrence periods: 1 Hour, 1 Day, 1 Week, 1 Month
- **AND** user clicks "Download Product Template" on the rental product list
- **THEN** a CSV file is downloaded with columns: `sap_article_code, name, type, categ_id, list_price, rent_ok, extra_hourly, extra_daily, uom_id, tracking, default_code, barcode, description_sale, 1 Hour, 1 Day, 1 Week, 1 Month`
- **AND** the file contains one example data row

#### Scenario: New recurrence period reflected in template
- **WHEN** an admin adds a new recurrence "2 Years" to `sale.temporal.recurrence`
- **AND** user downloads the product template
- **THEN** the CSV SHALL include a "2 Years" column

#### Scenario: Button only visible on rental product view
- **WHEN** user is on the general product list view (not rental)
- **THEN** the "Download Product Template" button SHALL NOT be visible

### Requirement: Download pricing CSV template
The system SHALL provide a separate button to download a pricing-only CSV template for updating pricing on existing products.

The template SHALL include:
- Fixed column: `sap_article_code`
- Dynamic columns: one per `sale.temporal.recurrence` record (same as product template)
- One example row

#### Scenario: Download pricing template
- **WHEN** user clicks "Download Pricing Template" on the rental product list
- **THEN** a CSV file is downloaded with columns: `sap_article_code, 1 Hour, 1 Day, 1 Week, ...` (all current recurrence periods)

#### Scenario: Pricing template used to update only pricing
- **WHEN** user imports a pricing-only CSV with just `sap_article_code` and pricing columns
- **THEN** the import controller SHALL update pricing without modifying other product fields
