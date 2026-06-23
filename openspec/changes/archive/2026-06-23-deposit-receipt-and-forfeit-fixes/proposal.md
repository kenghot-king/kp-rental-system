## Why

The rental deposit flow has correctness gaps: returning an order whose deposit was held (not paid
in cash) crashes with *"There's nothing left to pay…"*, the printed receipt shows the invoice date
rather than the date money actually changed hands, and there is no dedicated **ใบมัดจำ (Deposit
Certificate)** document. These block day-to-day deposit handling (forfeit, unhold, return) and
must be fixed for go-live.

## What Changes

- Add a **ใบมัดจำ (Deposit Certificate)** PDF based on the Thai invoice/receipt layout: title
  "ใบมัดจำ", no bottom signature/received block, "No." shows the Sale Order number, file name
  `Deposit Certificate-{SO no.}.pdf`.
- Make the ใบเสร็จรับเงิน/ใบกำกับภาษี **"Date" show the paid date** (the reconciled payment's date)
  instead of the invoice date. Fallback to the invoice date when no payment exists.
- Forfeiting a deposit keeps dating the **payment** (not the posted invoice) to the chosen
  forfeiture date, so the forfeit receipt automatically shows the forfeiture date.
- Treat **unhold (released) and forfeit (paid)** as deposit settlement so the order's deposit axis
  is satisfied and the order can reach **Complete**.
- **BREAKING (behavior):** on Return, a deposit credit note is created/auto-refunded **only when
  the deposit was paid in cash** (a real residual exists). A **held** deposit (released or
  forfeited) produces **no credit note** — fixing both the return crash and the forfeit-then-return
  double-refund.

Assumption (for now): no partial payments — 1 invoice = 1 payment = 1 receipt. True per-payment
receipts (one invoice → many receipts, VAT-per-payment, receipt running numbers) are out of scope
and deferred to a later change.

## Capabilities

### New Capabilities
- `deposit-certificate-document`: the ใบมัดจำ PDF — layout, title, removed signature block, SO-number "No.", and file name.
- `receipt-paid-date`: the receipt/tax-invoice "Date" reflects the reconciled payment's date, including the forfeiture date for forfeited deposits.
- `deposit-settlement-completion`: unhold and forfeit count as deposit settlement for order completion.
- `deposit-return-refund`: Return refund rules — credit note only for cash-paid deposits, none for held deposits.

### Modified Capabilities
<!-- None: no existing spec's requirements change. -->

## Impact

- Reports: `report/report_invoice_thai.xml`, plus a new deposit-certificate `ir.actions.report`
  with `print_report_name`.
- Models: `models/account_move.py` (paid-date helper), `models/sale_order_line.py` (return refund
  guard), `models/sale_order.py` (deposit-axis settlement — already partially via an uncommitted
  edit), `wizard/deposit_hold_forfeit_wizard.py` (verify forfeiture-date dating).
- User-facing: Return no longer crashes for held deposits; receipts show the paid/forfeiture date;
  a new ใบมัดจำ document is printable.
