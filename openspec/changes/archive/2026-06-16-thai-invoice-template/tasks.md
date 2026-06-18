## 1. Model — account.move extensions

- [x] 1.1 In `models/account_move.py`, add method `amount_in_thai_words(self)` that calls `num2words(self.amount_total, lang='th', to='currency')` and returns the string; guard with `if self.currency_id.name != 'THB': return ''`
- [x] 1.2 In `models/account_move.py`, override `_get_name_invoice_report(self)` to return `'ggg_rental.report_invoice_document'`

## 2. QWeb template — full Thai invoice layout

- [x] 2.1 Create `report/report_invoice_thai.xml`; add `<template id="report_invoice_document" inherit_id="account.report_invoice_document" primary="True">` with a full `position="replace"` on the root, wrapping everything in `<t t-call="web.external_layout">`
- [x] 2.2 Implement the company header section: logo (left), company name + address + Tel/Fax/Tax Id (center), Page X/Y counter (right) using `web.external_layout` header slot or custom div
- [x] 2.3 Implement the bilingual title block: centered, `ต้นฉบับ ใบแจ้งหนี้` / `INVOICE ORIGINAL`, bold
- [x] 2.4 Implement the two-column customer/invoice info block: left = Customer Name, Address, Customer code, Tax Id + branch; right = No., Date, Term of Payment, Due Date, Vendor Code (blank), Currency
- [x] 2.5 Implement the line items table: columns NO. / DESCRIPTION / VAT CODE / AMOUNT; iterate `o.invoice_line_ids.filtered(lambda l: l.display_type == 'product')`; VAT CODE = comma-join of `line.tax_ids.mapped('tax_group_id.name')`; AMOUNT = `line.price_subtotal`
- [x] 2.6 Implement VAT/NON-VAT subtotal computation in template: `vat_lines` = lines with `any(t.amount > 0 for t in line.tax_ids)`; `non_vat_lines` = the rest; display totals with "-" for zero values
- [x] 2.7 Implement WHT detection: `wht_lines = o.line_ids.filtered(lambda l: l.tax_line_id and l.tax_line_id.amount < 0)`; `wht_amount = abs(sum(wht_lines.mapped('amount_currency')))`; display "-" if zero
- [x] 2.8 Implement totals block (right-aligned): VAT Amount = `o.amount_tax` (positive taxes only), Grand Total = `o.amount_total`, Withholding Tax = `wht_amount`, Net Amount = `o.amount_total - wht_amount`
- [x] 2.9 Implement amount in Thai words row: `(THB) <t t-esc="o.amount_in_thai_words()"/>`, only render if `o.currency_id.name == 'THB'`
- [x] 2.10 Implement cheque payment note (bilingual Thai + English text, left-aligned lower section)
- [x] 2.11 Implement dual signature blocks: left = received-by block with dotted lines; right = "FOR [o.company_id.name]" + authorized signature block

## 3. Report wrapper override

- [x] 3.1 In `report/report_invoice_thai.xml`, add `<template id="report_invoice" inherit_id="account.report_invoice">` with an xpath `position="after"` the existing `t-call="account.report_invoice_document"` node to add: `<t t-elif="o._get_name_invoice_report() == 'ggg_rental.report_invoice_document'" t-call="ggg_rental.report_invoice_document" t-lang="lang"/>`

## 4. Registration

- [x] 4.1 Add `'report/report_invoice_thai.xml'` to the `data` list in `__manifest__.py` (before `wizard/` entries)

## 5. Verification

- [x] 5.1 Restart Odoo and upgrade `ggg_rental`; confirm no XML/QWeb parse errors in logs
- [x] 5.2 Open a posted `out_invoice` and print PDF; verify Thai layout renders correctly (title, columns, totals)
- [x] 5.3 Verify WHT amount: create an invoice with a 5% WHT tax (negative amount) and confirm WHT row and Net Amount are correct
- [x] 5.4 Verify amount in Thai words renders correct text for a round-number THB invoice
- [x] 5.5 Verify a zero-NON-VAT or zero-VAT invoice shows "-" in the respective subtotal row
