## Context

The Thai invoice report template (`report_invoice_thai.xml`) renders the same right-column header table for all move types (invoice, receipt, credit note). The ใบลดหนี้ currently shows: No., Date, Term of Payment, Due Date, Vendor Code, Currency — identical to a receipt.

For deposit refund credit notes, QA requires two additional header rows:
- `Reference:` → `o.ref` (set by code to `"Deposit refund: S00XXX"`)
- `เลขที่ใบเสร็จค่ามัดจำ:` (Deposit Receipt No.) → `o.reversed_entry_id.name` (the original deposit invoice, e.g. `INV/2026/00390`)

The CN line description is a Python string set in `_create_deposit_credit_note()` in `sale_order_line.py`.

## Goals / Non-Goals

**Goals:**
- Add Reference and เลขที่ใบเสร็จค่ามัดจำ rows to the CN header, visible only on `out_refund` documents
- Change deposit CN line description to Thai text

**Non-Goals:**
- Modifying the receipt or invoice header layout
- Changing any other CN type (non-deposit refunds)

## Decisions

**Conditional rows using `t-if`**: Add the two new rows inside the right-column header table, wrapped in `<t t-if="o.move_type == 'out_refund'">`. This keeps normal receipts/invoices unchanged.

**`reversed_entry_id.name` for deposit invoice number**: The CN is created with `reversed_entry_id = deposit_invoice.id`, so `o.reversed_entry_id.name` reliably gives the original deposit invoice number (`INV/XXXX/XXXXX`).

**Thai-only description**: The line description change from `_create_deposit_credit_note()` removes the English product/quantity interpolation entirely and replaces it with the fixed Thai phrase. The product and quantity context is already conveyed by other fields on the CN (partner, amount, linked invoice).

## Risks / Trade-offs

- [out_refund catch-all] Any non-deposit out_refund on this template will also show the new rows — mitigated because `o.ref` and `o.reversed_entry_id` would simply be blank/empty for non-deposit CNs, rendering the rows empty but harmless. Optionally wrap in a stricter condition if needed later.
- [Description change] The Thai description removes the product name and qty fraction — acceptable per business requirement; original English string was auto-generated and not meaningful to Thai-speaking staff.
