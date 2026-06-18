## Why

Thai tax practice treats a paid customer invoice as a receipt, not an invoice: if the document contains VAT items it serves as a combined "ใบเสร็จรับเงิน/ใบกำกับภาษี" (Receipt/Tax Invoice), otherwise as a plain "ใบเสร็จรับเงิน" (Receipt). The current `thai-invoice-template` always prints the header "ต้นฉบับ ใบแจ้งหนี้ / INVOICE ORIGINAL" regardless of payment or VAT status, which does not match how the business issues documents to customers. In practice, unpaid invoices are never printed — only paid receipts are handed over — so the print output must be gated on the payment state and the header must reflect receipt semantics.

## What Changes

- **BREAKING** Remove the fixed bilingual "ต้นฉบับ ใบแจ้งหนี้ / INVOICE ORIGINAL" title from the Thai invoice template. Replace with a conditional Thai-only title:
  - `out_invoice` with any line carrying a tax of `amount > 0` → "ใบเสร็จรับเงิน/ใบกำกับภาษี"
  - `out_invoice` with no such line (including VAT 0%) → "ใบเสร็จรับเงิน"
  - `out_refund` → "ใบลดหนี้"
- Block printing of any `out_invoice` whose `payment_state != 'paid'`. Attempting to print such an invoice (UI button, direct URL, email preview, any path that renders the PDF) raises `UserError`.
- `out_refund` prints remain available regardless of payment state.
- No English subtitle in the new titles for now (Thai only).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `thai-invoice-pdf`: Replace the fixed bilingual title requirement with a conditional receipt/credit-note title, and add a payment-state gate on printing `out_invoice`.

## Impact

- **`addons/ggg_rental/report/report_invoice_thai.xml`** — remove the fixed title block, add conditional title logic driven by `move_type`, `payment_state`, and VAT presence (the existing `vat_lines` computation already supplies the signal).
- **`addons/ggg_rental/models/account_move.py`** — extend `_get_name_invoice_report()` to raise `UserError` when `move_type == 'out_invoice'` and `payment_state != 'paid'`.
- **Operational impact**: users who previously printed unpaid invoices for internal use will lose that ability. Confirmed with stakeholder — not a supported workflow.
- No schema changes, no new models, no new dependencies.
