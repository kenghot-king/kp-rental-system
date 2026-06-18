## Why

QA review of printed reports identified four display defects: the Thai Baht currency symbol ("B") overflows table cells in quotation, sale order, and Thai invoice PDFs; the rental contract has a redundant column header word and an unwanted acknowledgment section that clients do not need to sign on pickup.

## What Changes

- **Quotation & Sale Order PDF** (`sale.report_saleorder_document` override): remove the "B" currency symbol from unit price and subtotal columns — format amounts as plain `{:,.2f}` numbers.
- **Thai Invoice PDF** (`report_invoice_thai.xml`): remove "B" currency symbol from line-item AMOUNT column — switch from `monetary` widget to plain number format.
- **Rental Contract PDF** (`rental_contract_templates.xml`):
  - Rename column header "ยอดรวม" → "รวม" in the rental items table.
  - Remove the entire "การรับทราบและยืนยัน" (Acknowledgment & Confirmation) page/section.

## Capabilities

### New Capabilities
- `report-amount-formatting`: Controls how monetary amounts are rendered in PDF report templates — plain numbers without currency symbol vs. Odoo monetary widget.

### Modified Capabilities
<!-- No existing spec-level behavior changes -->

## Impact

- `addons/ggg_rental/report/rental_order_report_templates.xml` — new inherited template overriding sale order amount cells
- `addons/ggg_rental/report/report_invoice_thai.xml` — line 147–149, monetary widget replaced
- `addons/ggg_rental/report/rental_contract_templates.xml` — line 110 header text, lines 223–244 block removed
