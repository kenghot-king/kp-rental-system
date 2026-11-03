## Why

Accounting uses **Rental > Reporting > By Item** to check invoice lines, but the report only includes customer invoices. They cannot see the reverse invoice (credit note, RINV) for an order that has one, so they have to check those documents elsewhere. The customer requirement is to add RINV lines to this report so reverse invoices can be checked per order.

Adding credit notes to the list is not enough on its own. Credit note lines store positive amounts, so the report's totals would add them instead of subtracting them. In the QA backup of 2026-11-03, the posted Subtotal total would read 3,635,309.96 instead of the correct net 1,035,765.68. Their names also do not reliably show the order: 15 of 124 posted credit notes have no order number in their reference.

## What Changes

- Include customer credit notes (`out_refund`) in the By Item report alongside customer invoices.
- Show Subtotal and Tax as negative on credit note lines, so column and group totals are net. Unit Price and Quantity stay positive, as printed on the document.
- Add an **Order** column that can be searched and grouped by.
- Add a **Reversal Of** column showing the original invoice on a credit note.
- Add By Item filters for Invoices, Credit Notes and the `Reversed` payment status, and give `Reversed` its own badge colour.
- Open the report on Posted documents by default. Removing the filter shows draft and cancelled documents.

### Scope

- **Lifecycle stages:** read-only reporting over the invoicing and return/refund stages.
- **Accounting and payments:** reads existing documents only. No journal entries, payments or existing amounts change.
- **Deposits:** deposit credit notes are displayed, but when they are created does not change. Released or forfeited holds still produce no credit note, as defined by `deposit-return-refund`.
- **Stock, access control and Thai documents:** not affected.

### Non-goals

- Late fee handling, including fee products being rentable and unbilled fees. This needs a business decision and will be a separate change.
- Limiting the report to rental orders. It does not do this today, so any customer invoice or credit note appears.
- Changes to printed credit notes or other reports.

## Capabilities

### New Capabilities

- `rental-invoice-by-item-report`: which documents the By Item report includes, how credit note amounts and totals are shown, and how lines trace back to their order and original invoice.

### Modified Capabilities

None. The report has no existing spec. `deposit-return-refund` and `deposit-settlement-completion` are relied on but not changed. The most recent related change is `2026-06-23-deposit-receipt-and-forfeit-fixes`, which set the rule that holds produce no credit note.

## Impact

- **Module:** `ggg_rental` only.
- **Models:** `account.move.line` gains stored fields for signed Subtotal, signed Tax and Order. The unstored `tax_amount` field, used only by this report, is removed.
- **Views:** `views/rental_invoice_report_views.xml` (list, action and a new By Item search view).
- **Upgrade:** upgrading the module fills the new columns for existing journal items. No existing values change and no migration script is needed.
- **Tests and docs:** a new test file in `addons/ggg_rental/tests/` and a report section in `documents/rental_workflow.md`.
- **Dependencies:** none added.
