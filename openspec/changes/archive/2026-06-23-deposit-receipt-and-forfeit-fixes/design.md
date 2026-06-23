## Context

The rental deposit can be collected two ways (see `documents/CR/hold_payment.md`):

- **Cash** (e.g. EDC journal): a real payment posts and the deposit invoice becomes `paid`.
- **Hold** (HLD journal): a pre-authorization `account.payment` is created in a non-posted state;
  no journal entry exists and the deposit invoice stays **unpaid** until the hold is forfeited.

A hold is later resolved by **unhold** (`hold_state = released`) or **forfeit** (wizard posts the
hold payment, invoice → `paid`). `is_rental_deposit` is only a marker flag; the deposit invoice
posts to the product's ordinary income account.

Current defects:
- Return calls `account.payment.register(...).create({})` to auto-refund the deposit credit note
  (`sale_order_line.py:561-566`). For a held deposit there is no cash residual, so the register
  raises *"There's nothing left to pay…"* and aborts the Return.
- The receipt "Date" binds to `o.invoice_date` (`report_invoice_thai.xml:97`), not the date money
  moved; forfeit dates only the payment, so a re-dating of the invoice would be needed to surface
  the forfeiture date on the printout.
- No ใบมัดจำ document exists in the invoice/receipt layout.

## Goals / Non-Goals

**Goals:**
- A ใบมัดจำ PDF reusing the Thai invoice layout, with the deposit-specific title/number/file name
  and no signature block.
- Receipt "Date" reflects the paid (payment) date; forfeit surfaces the forfeiture date without
  touching the posted invoice.
- Unhold/forfeit settle the deposit axis so orders can complete.
- Return never crashes for held deposits and never double-refunds a forfeited deposit.

**Non-Goals:**
- True per-payment receipts (1 invoice → N receipts), VAT-per-payment split, receipt running
  numbers — deferred to a later change.
- Reworking the deposit's chart-of-accounts treatment (income vs liability).
- Supporting partial payments (explicitly assumed absent for now).

## Decisions

### D1: Receipt Date = reconciled payment date, not invoice date

Add a computed helper on `account.move` returning the reconciled payment's date (from
`matched_payment_ids` / `reconciled_payment_ids`), and bind the receipt "Date" to it, falling back
to `invoice_date`. With no partial payments there is exactly one payment, so "the" paid date is
unambiguous.

- **Why not re-date the posted invoice?** Setting `invoice_date` on a posted move can clash with
  accounting period/lock dates and rewrites a legal document's date. Dating the *payment* is both
  safer and already what the forfeit wizard does.
- **Consequence:** forfeit needs no new code for the date — the forfeit payment is dated to the
  forfeiture date, and it is the payment that reconciles the invoice, so the receipt shows it.

### D2: Return refund gated on real residual (deposit type)

In `_create_deposit_credit_note`, create + auto-refund a credit note only when the deposit invoice
has an outstanding cash residual to refund. Held deposits (released or forfeited) are skipped.

- **Why:** a held deposit captured no cash, so a credit note nets to zero residual and the payment
  register fails; a forfeited deposit was intentionally kept, so refunding it is wrong.
- **Alternative considered:** wrap the payment register in try/except. Rejected — it hides the
  forfeit double-refund and still posts a spurious credit note.

### D3: Deposit settlement axis includes unhold/forfeit

Keep the existing (uncommitted) `sale_order.py:337` logic: the deposit axis is settled when the
deposit invoice is `paid` (forfeit/cash) or its hold is `released`/`cancelled` (unhold). Verify and
retain rather than re-implement.

### D4: ใบมัดจำ as a layout variant + dedicated report action

Reuse the `ggg_report_invoice_document` Thai layout. Branch the title to "ใบมัดจำ" and hide the
signature block for deposit documents, and show the linked SO number in "No.". Add a dedicated
`ir.actions.report` with `print_report_name` producing `Deposit Certificate-{SO no.}.pdf`.

- **Why a variant, not a brand-new template?** The desired output is the Thai invoice with three
  edits; duplicating the layout would create drift.

## Risks / Trade-offs

- [A deposit invoice could in theory have several reconciled payments] → Under the no-partial-
  payment assumption this cannot happen; if it ever does, the helper takes the latest payment date.
- [Distinguishing "cash-paid" from "held" deposit at return time] → Use the existing hold-state and
  payment-state signals already on the deposit invoice; do not infer from amounts.
- [ใบมัดจำ reuses the receipt template, which is print-gated to paid invoices] → Confirm the
  certificate is intended for the paid/forfeited deposit invoice; otherwise the gate must be relaxed
  for the certificate path.

## Migration Plan

- Pure code/report change; no data migration. Deploy by upgrading the module so assets and report
  actions reload. Rollback = revert the module.

## Open Questions

- None blocking. (Income-vs-liability accounting for deposits and per-payment receipts are
  acknowledged as separate future work, not part of this change.)
