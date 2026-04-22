## ADDED Requirements

### Requirement: Thai invoice template replaces default for all out_invoices
The system SHALL render all `out_invoice` PDF prints using the Thai-format template `ggg_rental.report_invoice_document` instead of the Odoo default or l10n_th template. The override SHALL be applied by returning `'ggg_rental.report_invoice_document'` from `account.move._get_name_invoice_report()`.

#### Scenario: Print invoice uses Thai template
- **WHEN** a user prints any `out_invoice` document
- **THEN** the PDF SHALL render using the Thai-format layout (not the standard Odoo or l10n_th layout)

---

### Requirement: Invoice header shows company info and page counter
The template SHALL render a header containing: company logo (if set), company name, office type (HEAD OFFICE), address, phone, fax, tax ID, and a "Page X / Y" counter in the top-right corner.

#### Scenario: Header renders company data
- **WHEN** an invoice PDF is generated
- **THEN** the header SHALL display the company's name, address, Tel, Fax, and Tax ID from `o.company_id`

#### Scenario: Page counter appears
- **WHEN** an invoice PDF is generated
- **THEN** the top-right corner SHALL show "Page X / Y" using the report engine's page counter

---

### Requirement: Bilingual title block
The template SHALL display a centered title block with Thai text "ต้นฉบับ ใบแจ้งหนี้" on the first line and "INVOICE ORIGINAL" on the second line, styled bold.

#### Scenario: Title renders bilingual
- **WHEN** an invoice PDF is generated
- **THEN** the centered title block SHALL contain both "ต้นฉบับ ใบแจ้งหนี้" and "INVOICE ORIGINAL"

---

### Requirement: Customer and invoice info block (two-column)
The template SHALL render a two-column info block below the title:
- **Left column**: Customer Name (`partner_id.name`), Address (`partner_id` contact widget), Customer code (`partner_id.ref`), Tax Id (`partner_id.vat`) + branch name (`partner_id.l10n_th_branch_name`)
- **Right column**: No. (`o.name`), Date (`o.invoice_date`), Term of Payment (`o.invoice_payment_term_id.name`), Due Date (`o.invoice_date_due`), Vendor Code (blank), Currency (`o.currency_id.name`)

#### Scenario: Customer fields render
- **WHEN** the partner has a name, ref, vat, and branch name set
- **THEN** all four customer fields SHALL appear in the left column

#### Scenario: Invoice reference fields render
- **WHEN** an invoice is posted
- **THEN** No., Date, Due Date, and Currency SHALL appear in the right column

---

### Requirement: Line items table with VAT CODE column
The template SHALL render a table with columns: NO., DESCRIPTION, VAT CODE, AMOUNT. Each row corresponds to one `invoice_line_ids` entry with `display_type == 'product'`. VAT CODE SHALL be the tax group name of the line's taxes (comma-joined if multiple). AMOUNT SHALL be `line.price_subtotal` formatted with thousand separators.

#### Scenario: Product lines render with VAT code
- **WHEN** an invoice has product lines with taxes applied
- **THEN** each line SHALL show its row number, description, tax group name, and subtotal amount

#### Scenario: Lines with no tax show empty VAT CODE
- **WHEN** an invoice line has no taxes
- **THEN** the VAT CODE cell SHALL be empty

---

### Requirement: VAT / NON-VAT subtotal split
The template SHALL display two subtotal rows:
- "Total Amount For NON-VAT": sum of `price_subtotal` for lines with no positive-amount tax
- "Total Amount For VAT": sum of `price_subtotal` for lines with at least one positive-amount tax

A zero subtotal SHALL display as "-".

#### Scenario: NON-VAT lines sum correctly
- **WHEN** some lines have no VAT tax
- **THEN** "Total Amount For NON-VAT" SHALL equal the sum of those lines' price_subtotal

#### Scenario: VAT lines sum correctly
- **WHEN** some lines have a positive-amount tax
- **THEN** "Total Amount For VAT" SHALL equal the sum of those lines' price_subtotal

#### Scenario: Zero subtotal shown as dash
- **WHEN** there are no NON-VAT lines
- **THEN** "Total Amount For NON-VAT" SHALL display "-" instead of 0.00

---

### Requirement: VAT Amount, Grand Total, WHT, Net Amount
The template SHALL display:
- "VAT Amount": `o.amount_tax` (only positive tax amounts, excluding WHT)
- "Grand Total": `o.amount_total` (including VAT, before WHT deduction)
- "Withholding Tax": absolute value of negative-amount tax lines (`o.line_ids` where `tax_line_id.amount < 0`); displays "-" if zero
- "Net Amount": Grand Total minus Withholding Tax

#### Scenario: WHT detected and deducted
- **WHEN** an invoice has a tax with negative amount (e.g., -5% WH R)
- **THEN** "Withholding Tax" SHALL display the absolute WHT amount and "Net Amount" SHALL equal Grand Total minus WHT

#### Scenario: No WHT
- **WHEN** an invoice has no negative-amount taxes
- **THEN** "Withholding Tax" SHALL display "-" and "Net Amount" SHALL equal Grand Total

---

### Requirement: Amount in Thai words (THB only)
The template SHALL display the invoice total in Thai words in the format `(THB) [words]` using `num2words(o.amount_total, lang='th', to='currency')`. This row SHALL only appear when `o.currency_id.name == 'THB'`.

#### Scenario: Thai words for THB invoice
- **WHEN** the invoice currency is THB
- **THEN** the amount in words row SHALL display Thai text representing the total amount

#### Scenario: Non-THB invoice omits Thai words
- **WHEN** the invoice currency is not THB
- **THEN** the amount in words row SHALL not render Thai words

---

### Requirement: Cheque payment note (bilingual)
The template SHALL display a Thai and English cheque payment note in the lower-left area: "ในกรณีชำระด้วยเช็ค โปรดสั่งจ่ายและขีดคร่อมในนามบริษัทเท่านั้น" followed by the English translation.

#### Scenario: Cheque note renders
- **WHEN** an invoice PDF is generated
- **THEN** the cheque payment note SHALL appear in both Thai and English

---

### Requirement: Dual signature blocks
The template SHALL render two signature blocks at the bottom:
- **Left**: "ได้รับสินค้า / บริการตามรายการข้างบนไว้ถูกต้องในสภาพเรียบร้อย" / "Received the above goods/ services in good condition" / dotted signature line / "ผู้รับสินค้า / บริการ : Received by" / "วันที่ : Date ......./......./..............."
- **Right**: "FOR [o.company_id.name]" / dotted signature line / "ผู้รับมอบอำนาจ / Authorized Signature" / "วันที่ : Date ......./......./..............."

#### Scenario: Signature blocks render with company name
- **WHEN** an invoice PDF is generated
- **THEN** the right signature block SHALL display "FOR [company name]" using `o.company_id.name`
