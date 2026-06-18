## ADDED Requirements

### Requirement: SAP article code field on product template
The system SHALL provide a `sap_article_code` field on `product.template` that serves as a unique business key for cross-system product identification.

The field SHALL be:
- Type: Char
- Required: True (at Python level; nullable at DB level for migration)
- Indexed: True
- Unique: Enforced via SQL constraint
- Copy: False (not copied when duplicating products)
- Displayed on product form and tree views

#### Scenario: Creating a product with SAP article code
- **WHEN** a user creates a new rental product with `sap_article_code` = "SAP-12345"
- **THEN** the product is created with the code stored and visible on the form

#### Scenario: Duplicate SAP article code rejected
- **WHEN** a user creates a product with `sap_article_code` = "SAP-12345" and another product already has that code
- **THEN** the system SHALL raise a validation error indicating the code must be unique

#### Scenario: SAP article code required on save
- **WHEN** a user tries to save a rental product without a `sap_article_code`
- **THEN** the system SHALL raise a validation error indicating the field is required

#### Scenario: SAP article code not copied on duplicate
- **WHEN** a user duplicates an existing product
- **THEN** the `sap_article_code` field SHALL be empty on the copied product
