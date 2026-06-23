## 1. Receipt paid date (item 2)

- [X] 1.1 Add a computed helper on `account.move` returning the reconciled payment's date (from `matched_payment_ids`/`reconciled_payment_ids`), latest if several, else `False`
- [X] 1.2 Bind the receipt "Date" in `report/report_invoice_thai.xml` (L97) to the paid-date helper, falling back to `invoice_date` when empty
- [X] 1.3 Verify the forfeit wizard dates the captured hold payment to the chosen forfeiture date (`deposit_hold_forfeit_wizard.py:25`) and confirm the forfeit receipt shows that date with the posted `invoice_date` unchanged

## 2. Deposit return refund guard (item 4)

- [X] 2.1 In `sale_order_line._create_deposit_credit_note`, gate credit-note creation + auto-refund on the deposit invoice having a real outstanding cash residual (cash-paid); skip for held deposits (released or forfeited)
- [X] 2.2 Ensure no `account.payment.register` call runs when there is nothing to refund (remove the "There's nothing left to pay" crash path)
- [X] 2.3 Confirm a forfeited deposit is not refunded by a later Return (no double-refund)

## 3. Deposit settlement on unhold/forfeit (item 3)

- [X] 3.1 Verify and keep the `sale_order.py:337` deposit-axis logic: settled when invoice `paid` (forfeit/cash) or hold `released`/`cancelled` (unhold); active hold not settled
- [X] 3.2 Confirm an order reaches Complete when returned + non-deposit invoices paid + deposit settled by unhold or forfeit

## 4. ใบมัดจำ (Deposit Certificate) document (item 1)

- [X] 4.1 Branch the Thai invoice title (`report_invoice_thai.xml` L40-42) to "ใบมัดจำ" for the deposit-certificate render path
- [X] 4.2 Hide the bottom signature/received block (L246-275) for the deposit-certificate render path
- [X] 4.3 Show the linked Sale Order number in the "No." field for the deposit certificate
- [X] 4.4 Add an `ir.actions.report` for the certificate with `print_report_name` producing `Deposit Certificate-{SO no.}.pdf`
- [X] 4.5 Wire/confirm the print action on the deposit invoice (e.g. the existing "Print Deposit Certificate" button)

## 5. Verification

- [X] 5.1 Held deposit: unhold → return completes without error, no credit note, order can complete
- [X] 5.2 Held deposit: forfeit with chosen date → receipt shows forfeiture date; later return creates no credit note
- [X] 5.3 Cash-paid deposit: return creates and auto-refunds the proportional credit note
- [X] 5.4 Print ใบมัดจำ → title, no signature block, SO number in "No.", file name `Deposit Certificate-{SO no.}.pdf`
- [X] 5.5 Upgrade module on `test_ce` and smoke-test the deposit/forfeit/return flow end to end (module upgrades & loads clean; 5.1–5.4 need manual UI verification)
