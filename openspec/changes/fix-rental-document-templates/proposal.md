## Why

QA review of printed rental documents revealed six visual and data-correctness defects across the rental contract, sale quotation, and Thai tax invoice templates. These need to be fixed before the system goes to production users.

## What Changes

- **Rental contract — lessee box height**: The ผู้เช่า (lessee) border box does not match the height of the ผู้ให้เช่า (lessor) box in PDF output because WeasyPrint does not honour Bootstrap `h-100` in flexbox columns. Replace the Bootstrap row/col layout with an HTML `<table>` for the two-party block.
- **Rental contract — document date**: The "วันที่" field currently shows `date_order` (order creation date). It must show the rental start date (`rental_start_date`) formatted as `dd/MM/yyyy`.
- **Rental contract — company address overlap on page 2+**: The `web.external_layout` repeats the company address header on every PDF page; insufficient page-body top margin causes the header to overlap content on pages 2 and 3. Add explicit top-margin CSS so the body clears the running header.
- **Rental contract — signature section page overflow**: Signature/acknowledgement text overflows onto subsequent pages with overlapping characters. Force a page break before the signature section.
- **Sale quotation — remove Terms & Conditions link**: The quotation report still renders the "เงื่อนไขและข้อกำหนด" (T&C) URL block. Suppress it via an XPath override that hides the note/T&C element.
- **Thai tax invoice — remove table borders from customer info and payment sections**: The outer customer-info table and the payment-information block display visible cell borders that should be removed (borderless layout).

## Capabilities

### New Capabilities

- `rental-contract-layout`: Visual layout correctness for the rental contract PDF — equal-height party boxes, correct date, proper page margins, and forced page break before signatures.
- `quotation-no-tc`: Quotation PDF renders without the Terms & Conditions URL block.
- `thai-invoice-borderless-header`: Thai tax invoice customer-info and payment-info sections render without table borders.

### Modified Capabilities

<!-- No existing spec-level requirement changes -->

## Impact

- `addons/ggg_rental/report/rental_contract_templates.xml` — parties table, date field, page-margin CSS, signature page break
- `addons/ggg_rental/report/report_invoice_thai.xml` — customer-info and payment-info table border styles
- Sale order report — XPath override to suppress T&C note (likely in `addons/ggg_rental/` or a new override template)
