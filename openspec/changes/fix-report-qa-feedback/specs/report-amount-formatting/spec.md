## ADDED Requirements

### Requirement: Sale order PDF amounts display without currency symbol
The sale order and quotation PDF SHALL render unit price and line subtotal amounts as plain formatted numbers (e.g., "850.00") without appending the currency symbol or name.

#### Scenario: Quotation PDF amount column
- **WHEN** a quotation PDF is generated for a THB order
- **THEN** the unit price column and subtotal column show numbers like "850.00" with no "B" suffix

#### Scenario: Sale order PDF amount column
- **WHEN** a confirmed sale order PDF is generated
- **THEN** all monetary amount cells in the lines table show plain numbers without currency symbol

### Requirement: Thai invoice PDF line amounts display without currency symbol
The Thai invoice PDF (ใบเสร็จรับเงิน/ใบกำกับภาษี) SHALL render the AMOUNT column for each line item as a plain formatted number without currency symbol.

#### Scenario: Line item amount column
- **WHEN** a Thai invoice PDF is generated
- **THEN** the AMOUNT column shows values like "794.39" without "B" or "฿"

#### Scenario: Totals section unaffected
- **WHEN** a Thai invoice PDF is generated
- **THEN** the totals section (Total Amount For VAT, Grand Total, Net Amount) continues to render as plain numbers (already correct)

### Requirement: Rental contract column header uses short label
The rental items table in the rental contract PDF SHALL use "รวม" (not "ยอดรวม") as the column header for the line subtotal column.

#### Scenario: Rental items table header
- **WHEN** a rental contract PDF is generated
- **THEN** the fourth column header reads "รวม"

### Requirement: Rental contract omits acknowledgment section
The rental contract PDF SHALL NOT include the "การรับทราบและยืนยัน" (Acknowledgment and Confirmation) section.

#### Scenario: Contract PDF page count
- **WHEN** a rental contract PDF is generated
- **THEN** the document does not contain a page with the "การรับทราบและยืนยัน" heading or its signature blocks
