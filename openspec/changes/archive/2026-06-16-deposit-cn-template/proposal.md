## Why

QA feedback (Release 1, 5 May 2026, page 3) identified two issues on the ใบลดหนี้ (Credit Note) printed for deposit refunds: the header is missing the Reference field and the original deposit invoice number, and the line description uses a generic English string instead of the Thai text required by the business.

## What Changes

- Add `Reference:` row to the ใบลดหนี้ header (right column), showing `o.ref` — only when `move_type == 'out_refund'`
- Add `เลขที่ใบเสร็จค่ามัดจำ:` row to the ใบลดหนี้ header, showing the original deposit invoice number (`o.reversed_entry_id.name`) — only when `move_type == 'out_refund'`
- Change the deposit CN line description from `"Deposit refund - {product} ({returned}/{total} returned)"` to `"คืนเงินมัดจำตามเงื่อนไขที่ระบุในสัญญาเช่า"`

## Capabilities

### New Capabilities
- `deposit-cn-template`: Credit note header fields and line description for deposit refunds

### Modified Capabilities
- None

## Impact

- `addons/ggg_rental/report/report_invoice_thai.xml` — add two conditional header rows for `out_refund` move type
- `addons/ggg_rental/models/sale_order_line.py` — change `name` value in `_create_deposit_credit_note()` at line 536
