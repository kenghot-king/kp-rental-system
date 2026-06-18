## Context

Odoo's monetary field widget (`t-options='{"widget":"monetary","display_currency":...}'`) appends the currency symbol (e.g., "B" for THB) after the formatted number. For Thai Baht, this renders as "794.39 B". In narrow table columns the symbol overflows the cell boundary, which QA flagged as a visual defect. The fix is to bypass the monetary widget and format numbers directly as `'{:,.2f}'.format(value)`.

Three templates are affected:
- Standard Odoo sale order report (inherited in `rental_order_report_templates.xml`)
- Custom Thai invoice (`report_invoice_thai.xml`)
- Rental contract (`rental_contract_templates.xml`)

## Goals / Non-Goals

**Goals:**
- Remove currency symbol from all amount columns in quotation, sale order, and Thai invoice PDFs
- Fix rental contract column header "ยอดรวม" → "รวม"
- Remove the "การรับทราบและยืนยัน" section from the rental contract

**Non-Goals:**
- Do not change amount display in the Odoo backend UI (only PDF reports)
- Do not change footer summary labels ("ยอดรวมค่าเช่า", "ยอดรวมเงินประกัน") — column header only
- Do not touch other report templates not mentioned in the QA feedback

## Decisions

**1. Sale order override approach: xpath inheritance, not full template copy**
- Override `sale.report_saleorder_document` via `<template inherit_id>` with targeted `<xpath>` replacements on the `td_product_subtotal` and `price_unit` cells.
- Alternative: full copy of the standard template — rejected because it would drift from upstream Odoo changes.

**2. Plain number format: Python `'{:,.2f}'.format()` via `t-esc`**
- Replace `t-field` + monetary widget with `t-esc="'{:,.2f}'.format(line.price_subtotal)"`.
- Alternative: CSS `::after` hiding — rejected because unreliable across PDF renderers.
- Alternative: custom monetary format on the currency record — rejected because it affects the entire system, not just reports.

**3. Rental contract acknowledgment removal: delete the block entirely**
- The `<div class="mt-5" style="page-break-before: always;">` block containing "การรับทราบและยืนยัน" is removed completely.
- No flag or conditional — QA confirmed it should always be gone.

## Risks / Trade-offs

- **Amounts lose currency context visually** → Acceptable; the document header already shows currency (THB), and the Thai invoice title makes context clear.
- **Sale order xpath may break on Odoo version upgrades** → Mitigation: xpath targets named `td` elements (`name="td_product_subtotal"`, `name="td_combo_price"`) which are stable identifiers in the Odoo sale report template.
- **Rental contract template is large (354KB)** → Read in offset chunks; the three touch points are at known lines (110, 123–127, 223–244).
