## Why

Two PDF report rendering bugs affect customer-facing documents: the quotation "Total" row displays a number instead of the label "Total", and the rental contract deposit section (เงินประกัน) renders on the same page as the rental items instead of starting on a new page.

## What Changes

- Fix the XPath selector in `sale_document_tax_totals_no_currency` to target only the amount `<strong>` element, not the label `<strong>Total</strong>`, so the label is preserved
- Add `page-break-before: always` to the deposit section `<div>` in the rental contract template so เงินประกัน always starts on a new page

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `rental-document-templates`: Quotation total label display and contract deposit page layout requirements are changing

## Impact

- `addons/ggg_rental/report/rental_order_report_templates.xml` — XPath fix for `sale_document_tax_totals_no_currency` template
- `addons/ggg_rental/report/rental_contract_templates.xml` — page-break style on deposit section div
