## 1. Fix Quotation Total Label

- [x] 1.1 In `rental_order_report_templates.xml`, update the XPath in `sale_document_tax_totals_no_currency` from `//tr[@class='o_total']//strong` to `//tr[@class='o_total']/td[last()]//strong`
- [x] 1.2 Verify quotation PDF renders "Total" label in the left column and formatted amount in the right column

## 2. Fix Rental Contract Deposit Page Break

- [x] 2.1 In `rental_contract_templates.xml`, add `style="page-break-before: always;"` to the deposit section `<div class="mb-4" t-if="deposit_lines">` at line 142
- [x] 2.2 Verify rental contract PDF starts the เงินประกัน section on a new page when deposit lines exist
- [x] 2.3 Verify contract PDF with no deposit lines generates no orphan page
