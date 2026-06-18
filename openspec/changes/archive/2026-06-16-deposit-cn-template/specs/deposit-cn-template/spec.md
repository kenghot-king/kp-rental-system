## ADDED Requirements

### Requirement: Credit note header shows Reference field
When printing a ใบลดหนี้ (`move_type == 'out_refund'`), the right-column header SHALL include a `Reference:` row displaying `o.ref`.

#### Scenario: Reference row visible on CN
- **WHEN** a ใบลดหนี้ PDF is generated
- **THEN** the header right column SHALL contain a row labelled "Reference:" with the value of `o.ref`

#### Scenario: Reference row absent on receipt
- **WHEN** a ใบเสร็จรับเงิน PDF is generated (`move_type != 'out_refund'`)
- **THEN** no "Reference:" row SHALL appear in the header

### Requirement: Credit note header shows original deposit invoice number
When printing a ใบลดหนี้, the right-column header SHALL include an `เลขที่ใบเสร็จค่ามัดจำ:` row displaying `o.reversed_entry_id.name` (the original deposit invoice number).

#### Scenario: Deposit receipt number row visible on CN
- **WHEN** a ใบลดหนี้ PDF is generated and `o.reversed_entry_id` exists
- **THEN** the header SHALL contain a row labelled "เลขที่ใบเสร็จค่ามัดจำ:" showing the reversed entry's name (e.g. `INV/2026/00390`)

#### Scenario: Row empty when no reversed entry
- **WHEN** a ใบลดหนี้ PDF is generated and `o.reversed_entry_id` is not set
- **THEN** the row SHALL render with an empty value (not error)

### Requirement: Deposit CN line description uses Thai text
The line description on a deposit refund credit note SHALL be `"คืนเงินมัดจำตามเงื่อนไขที่ระบุในสัญญาเช่า"` instead of the auto-generated English string.

#### Scenario: Thai description on deposit CN
- **WHEN** `_create_deposit_credit_note()` creates a credit note line
- **THEN** the line `name` field SHALL be `"คืนเงินมัดจำตามเงื่อนไขที่ระบุในสัญญาเช่า"`

#### Scenario: Description appears correctly on printed CN
- **WHEN** the ใบลดหนี้ PDF is generated
- **THEN** the DESCRIPTION column SHALL show `"คืนเงินมัดจำตามเงื่อนไขที่ระบุในสัญญาเช่า"`
