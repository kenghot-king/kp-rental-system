## MODIFIED Requirements

### Requirement: Quotation total row displays label and amount
The sale order / quotation PDF total row SHALL display the text "Total" as a label in the first column, and the formatted numeric amount (without currency symbol) in the second column. Both elements MUST be independently rendered.

#### Scenario: Total row shows label
- **WHEN** a quotation PDF is generated
- **THEN** the total row SHALL display "Total" as a text label in the left column

#### Scenario: Total row shows formatted amount
- **WHEN** a quotation PDF is generated
- **THEN** the total row SHALL display the numeric total (e.g., "2,321.00") in the right column without a currency symbol

#### Scenario: Label is not replaced by amount
- **WHEN** the `sale_document_tax_totals_no_currency` template override is applied
- **THEN** only the amount `<strong>` element SHALL be replaced, and the "Total" label `<strong>` element MUST remain unchanged

### Requirement: Rental contract deposit section starts on a new page
The เงินประกัน (deposit) section of the rental contract PDF SHALL always begin on a new printed page, separate from the rental items table above it.

#### Scenario: Deposit on new page
- **WHEN** a rental contract PDF is generated and deposit lines exist
- **THEN** the เงินประกัน section SHALL start at the top of a new page

#### Scenario: No deposit no page break
- **WHEN** a rental contract PDF is generated and no deposit lines exist
- **THEN** the deposit section SHALL not be rendered (no orphan page break)
