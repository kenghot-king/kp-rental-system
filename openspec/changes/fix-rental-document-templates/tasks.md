## 1. Rental Contract — Party Box Equal Height

- [x] 1.1 In `rental_contract_templates.xml` lines 44–57, replace the Bootstrap `<div class="row mb-4">` / `<div class="col-6">` party block with a two-cell `<table width="100%">` so WeasyPrint equalises cell heights automatically
- [ ] 1.2 Verify both lessor and lessee border boxes are the same height in the generated PDF when lessee has fewer address lines than lessor

## 2. Rental Contract — Document Date

- [x] 2.1 In `rental_contract_templates.xml` line 39, change `t-field="doc.date_order"` to `t-field="doc.rental_start_date"` keeping `t-options='{"widget": "date"}'`
- [ ] 2.2 Print a test contract and confirm the date shown matches the pickup/start date in `dd/MM/yyyy` format (Thai locale)

## 3. Rental Contract — Company Header Overlap

- [x] 3.1 Inside the `<style>` block in `rental_contract_templates.xml` (lines 8–24), add an `@page { margin-top: 55mm; }` rule so the body clears the running company-address header on all pages
- [ ] 3.2 Generate a multi-page contract (long T&C) and confirm no header/body text overlap on pages 2 and 3

## 4. Rental Contract — Signature Page Break

- [x] 4.1 Add `style="page-break-before: always;"` to the signature section `<div class="mt-5">` at line 215 of `rental_contract_templates.xml`
- [ ] 4.2 Confirm the acknowledgement/signature section always starts at the top of a new page

## 5. Sale Quotation — Remove T&C Block

- [x] 5.1 Identify the exact XPath target for the T&C / note block in `sale.report_saleorder_document` (check for `<p t-if="doc.note">` or the terms anchor element in the standard `sale` module template)
- [x] 5.2 Add a QWeb `<template inherit_id="sale.report_saleorder_document">` override in `ggg_rental` (or an existing override file) that sets `t-if="False"` on the T&C element
- [x] 5.3 Register the override template in `ggg_rental/__manifest__.py` data list if it is in a new file
- [ ] 5.4 Print a quotation PDF and confirm no "เงื่อนไขและข้อกำหนด" URL or note appears

## 6. Thai Tax Invoice — Remove Customer Info and Payment Borders

- [x] 6.1 In `report_invoice_thai.xml` line 38, remove any `border` shorthand from the outer customer-info `<table>` style attribute; confirm `border-collapse:collapse` is still present
- [x] 6.2 Remove `border` from all `<td>` elements in the customer-info left and right inner tables (lines 42–107) by adding `border: none;` to their inline styles or the containing table
- [x] 6.3 In the payment/totals block (lines 162–223), remove cell borders while preserving the intentional `border-top` separator lines on Grand Total and Net Amount rows
- [x] 6.4 Print a Thai invoice and confirm customer-info area and payment block have no visible grid lines; confirm Grand Total and Net Amount separator lines still appear
