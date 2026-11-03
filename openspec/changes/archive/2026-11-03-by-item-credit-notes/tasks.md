## 1. Model fields

- [x] 1.1 Add stored `signed_subtotal` and `signed_tax_amount` to `account.move.line` in `models/account_move_line.py`, negated for `out_refund`; verify with the amount tests in 4.2
- [x] 1.2 Add stored `sale_order_id`, computed from `sale_line_ids.order_id`, taking the first order if there are several; verify with the order tests in 4.3
- [x] 1.3 Add the related `reversed_entry_id` field; verify with the reversal test in 4.4
- [x] 1.4 Confirm `tax_amount` has no other references, then remove it and its compute

## 2. Report views

- [x] 2.1 Change the By Item action domain to include `out_invoice` and `out_refund`, keeping the `display_type = product` condition
- [x] 2.2 Add the Order and Reversal Of columns, switch Subtotal and Tax to the signed fields with their existing labels and totals, and keep the list read-only
- [x] 2.3 Add an info badge colour for the `reversed` payment status
- [x] 2.4 Add a primary By Item search view inheriting `account.view_account_move_line_filter` with priority above 16, containing Invoices, Credit Notes and Reversed filters, an Order search field and an Order group-by
- [x] 2.5 Set the search view on the action, with `search_default_posted` in its context

## 3. Documentation

- [x] 3.1 Add a By Item section to `documents/rental_workflow.md` covering credit note lines, negative amounts, net totals, the Posted default, and why held deposits have no RINV

## 4. Automated tests

- [x] 4.1 Add `addons/ggg_rental/tests/test_by_item_report.py`, register it in `tests/__init__.py`, and build fixtures using a rental order, its invoice and a tax
- [x] 4.2 Test signed amounts: a full credit note nets to 0.00 including tax, a partial one nets to the remainder, grouped totals by order are net, and quantity and unit price stay positive
- [x] 4.3 Test `sale_order_id` on an invoice, on an automatic deposit credit note, on a manual credit note, and on a document with no order
- [x] 4.4 Test `reversed_entry_id` on a credit note, an invoice, and a credit note with no original invoice
- [x] 4.5 Test the action's domain includes both document types and excludes tax lines, receivable lines and vendor bills
- [x] 4.6 Test a released or forfeited hold deposit produces no credit note line in the report domain
- [x] 4.7 Test creating these documents leaves the stored debit, credit, balance, unit price and `price_subtotal` unchanged

## 5. Verification

- [x] 5.1 Run `python3 scripts/verify_addons.py` and the JavaScript syntax check from `AGENTS.md`, with no errors
- [x] 5.2 Upgrade `ggg_rental` and run its test suite in the local `test_ce` database, as in `AGENTS.md`, with no failures
- [x] 5.3 Confirm on a non-production copy that existing lines get signed values after the upgrade, and that debit, credit and balance totals match before and after

## 6. Manual QA (record results)

- [x] 6.1 Open Reporting > By Item: only posted documents show, and totals are net
- [x] 6.2 Return a cash-paid deposit item: the RINV line shows a negative Subtotal, the Order and Reversal Of values, and nets to zero against the deposit invoice when grouped by Order
- [x] 6.3 Create a manual credit note from a rental invoice: its lines show the same Order and the original invoice
- [x] 6.4 Release a held deposit and return the item: no RINV line appears
- [x] 6.5 Remove the Posted filter: draft and cancelled documents appear with their status
- [x] 6.6 Apply the Invoices, Credit Notes and Reversed filters, and check the Reversed badge colour
- [x] 6.7 Open Accounting > Journal Items: the new filters are absent, and the existing screen behaves as before
- [x] 6.8 Export the report to Excel: signed amounts and the new columns are correct, and check for saved exports that use `tax_amount`
- [x] 6.9 Have accounting confirm the report meets the requirement on a real order with a credit note

### QA results (2026-11-03, local `test_ce`, read-only browser check)

- **6.1:** Opens with the Posted filter on, 120 lines. RINV lines show negative Subtotal.
- **6.2 (partly checked):** Not run through the Return screen. Existing `RINV/2026/00019` shows -2,000.00 with Order and Reversal Of, and its order nets to 300.00 with 21.00 tax when grouped. The automated test covers the return route.
- **6.5:** Removing Posted raises the count from 120 to 135 lines.
- **6.6 (partly checked):** The Credit Notes filter shows 19 lines totalling -1,092,394.76 and -75,039.62 tax, matching the database. The Reversed filter is offered but `test_ce` has no reversed invoices, so the badge colour has not been seen.
- **6.7:** Journal Items does not offer the new filters and still offers Paid.
- **6.8 (partly checked):** No saved exports or filters use `tax_amount` in `test_ce`. Other databases and the Excel export are unchecked.
- **Upgrade (5.3):** A fingerprint of debit, credit, balance, subtotal and unit price on all 503 journal lines is identical before and after. No line has an empty signed value.

The notes above are from the read-only browser check. Tasks 6.2, 6.3, 6.4, 6.6, 6.8 and 6.9 were ticked on 2026-11-03 after the project owner reported that testing had passed. No per-task results were recorded for them.
