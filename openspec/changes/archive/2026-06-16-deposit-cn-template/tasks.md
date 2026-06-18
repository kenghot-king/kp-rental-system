## 1. Report Template

- [ ] 1.1 In `report_invoice_thai.xml`, add a `Reference:` header row inside the right-column table, wrapped in `<t t-if="o.move_type == 'out_refund'">`, displaying `o.ref`
- [ ] 1.2 In `report_invoice_thai.xml`, add an `เลขที่ใบเสร็จค่ามัดจำ:` header row below Reference, displaying `o.reversed_entry_id.name`, same `out_refund` condition
- [ ] 1.3 Verify receipt and invoice PDFs still show no Reference or เลขที่ใบเสร็จค่ามัดจำ rows

## 2. CN Line Description

- [ ] 2.1 In `sale_order_line.py` `_create_deposit_credit_note()` (~line 536), change the `name` value from the English interpolated string to `"คืนเงินมัดจำตามเงื่อนไขที่ระบุในสัญญาเช่า"`
- [ ] 2.2 Verify a deposit return generates a CN with the Thai description on the printed ใบลดหนี้
