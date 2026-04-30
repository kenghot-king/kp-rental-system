## 1. Sale Order / Quotation PDF — Remove Currency Symbol

- [x] 1.1 In `rental_order_report_templates.xml`, add an inherited template (`inherit_id="sale.report_saleorder_document"`) with xpath targeting `td[@name="td_product_subtotal"]` to replace monetary widget with `t-esc="'{:,.2f}'.format(line.price_subtotal)"` (and `line.price_total` for the `price_total` branch)
- [x] 1.2 Add a second xpath targeting the unit price cell (`line.price_unit`) to replace its monetary widget with plain `'{:,.2f}'.format(line.price_unit)`

## 2. Thai Invoice PDF — Remove Currency Symbol from Line Items

- [x] 2.1 In `report_invoice_thai.xml` line ~147–149, replace `<span t-field="line.price_subtotal" t-options='{"widget":"monetary","display_currency":o.currency_id}'/>` with `<span t-esc="'{:,.2f}'.format(line.price_subtotal)"/>`

## 3. Rental Contract — Column Header Fix

- [x] 3.1 In `rental_contract_templates.xml` line 110, change `<th class="text-end">ยอดรวม</th>` to `<th class="text-end">รวม</th>`

## 4. Rental Contract — Remove Acknowledgment Section

- [x] 4.1 In `rental_contract_templates.xml`, remove the entire `<div class="mt-5" style="page-break-before: always;">` block containing "การรับทราบและยืนยัน" (lines ~223–244)
