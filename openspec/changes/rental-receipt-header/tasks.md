## 1. Print gate on account.move

- [x] 1.1 In `addons/ggg_rental/models/account_move.py`, extend `_get_name_invoice_report()` to raise `UserError` with the Thai message when `self.move_type == 'out_invoice'` and `self.payment_state != 'paid'`; import `UserError` from `odoo.exceptions` and `_` from `odoo` for translation
- [x] 1.2 Verify the method adds `self.ensure_one()` if not already present, since the guard reads per-record fields

## 2. Template title block

- [x] 2.1 In `addons/ggg_rental/report/report_invoice_thai.xml`, replace the existing fixed title `ต้นฉบับ ใบแจ้งหนี้ / INVOICE ORIGINAL` with a conditional `<t t-if>/<t t-elif>/<t t-else>` block driven by `o.move_type` and the already-computed `vat_lines`
- [x] 2.2 Ensure the three branches render exactly: `ใบลดหนี้` (out_refund), `ใบเสร็จรับเงิน/ใบกำกับภาษี` (has any VAT line), `ใบเสร็จรับเงิน` (otherwise); no English subtitle on any branch
- [x] 2.3 Keep the outer `<div>` styling (centered, `font-size:13pt`, bold, existing margins) so document layout below is unchanged

## 3. Manual verification in Odoo

- [x] 3.1 Restart the Odoo service and upgrade the `ggg_rental` module
- [x] 3.2 Create a paid `out_invoice` with at least one 7% VAT line → print → header shows `ใบเสร็จรับเงิน/ใบกำกับภาษี`
- [x] 3.3 Create a paid `out_invoice` whose lines carry no positive-amount taxes (including a case with only VAT 0%) → print → header shows `ใบเสร็จรับเงิน`
- [x] 3.4 Create an unpaid `out_invoice` → click Print → confirm `UserError` popup with the Thai message; repeat by directly visiting `/report/pdf/account.report_invoice/<id>` → confirm the same error
- [x] 3.5 Create an `out_invoice` in `payment_state == 'in_payment'` → confirm print is blocked; same for `partial`
- [x] 3.6 Create an `out_refund` (credit note), both posted-unpaid and paid → print → header shows `ใบลดหนี้`, no error in either state
- [x] 3.7 Confirm the VAT/NON-VAT subtotal rows, WHT row, Thai-words row, signatures, and all other sections below the title still render identically to before

## 4. Regression sweep

- [x] 4.1 Re-print one existing paid invoice created before this change → confirm header updates to the correct receipt variant and layout below is unchanged
- [x] 4.2 Run `openspec validate rental-receipt-header --strict` and resolve any issues
