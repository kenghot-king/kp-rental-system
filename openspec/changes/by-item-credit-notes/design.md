## Context

See `proposal.md` for motivation and `specs/rental-invoice-by-item-report/spec.md` for required behaviour.

By Item is an `ir.actions.act_window` on `account.move.line`, defined in `views/rental_invoice_report_views.xml`. Its current state:

- **Domain:** `move_type = out_invoice` and `display_type = product`.
- **List:** a dedicated read-only view that sums `price_subtotal` and `tax_amount`.
- **Search:** no explicit search view, so it uses core `account.view_account_move_line_filter`. `ggg_rental` extends that view with payment status filters, so those filters also appear on other journal item screens.
- **Fields:** `tax_amount` and `invoice_payment_state` are unstored, defined in `models/account_move_line.py`. `tax_amount` is used only by this list.

Facts from core Odoo that shape the design:

- `price_subtotal` and `price_total` are positive on credit note lines. Core's invoice report multiplies by -1 for `out_refund`.
- Credit notes can be created two ways, and both link lines to sale order lines through `sale_line_ids`. The automatic deposit refund sets it directly (`sale_order_line.py`, `_create_deposit_credit_note`). The manual route copies it, because `_reverse_moves` uses `include_business_fields` and `sale` extends `_copy_data_extend_business_fields`.
- Grouped totals are calculated in the database, so a field must be stored to total or group correctly.

## Goals / Non-Goals

**Goals:**

- Net totals are correct in both flat and grouped views.
- Invoices and their reversals can be grouped by order, whichever way the credit note was created.
- New filters stay on this report only.

**Non-Goals:**

- Changing how or when credit notes are created.
- Changing core fields, stored accounting amounts, or the existing payment status filters on other screens.

## Decisions

### 1. Add stored signed fields rather than changing existing ones

Add to `account.move.line`:

- `signed_subtotal`: `price_subtotal`, negated for `out_refund`.
- `signed_tax_amount`: `price_total - price_subtotal`, negated for `out_refund`.

Both are stored `Monetary` fields using `currency_id`, and depend on `price_subtotal`, `price_total` and `move_id.move_type`. The list shows them under the existing Subtotal and Tax labels. `tax_amount` is removed because nothing else uses it.

Alternatives considered:

- **Negated `balance`:** already stored, but it is in company currency, a list column cannot negate it, and there is no equivalent for tax.
- **Unstored compute:** cannot produce grouped totals.
- **`direction_sign`:** covers more document types than this report needs. An explicit `out_refund` check is clearer.

### 2. Add a stored Order field

Add `sale_order_id`, a stored `Many2one` to `sale.order`, computed from `sale_line_ids.order_id`, with label "Order". If a line links to more than one order, it takes the first. This is rare, and the line remains visible.

Storing it allows grouping and direct searching. Reading the order from `ref` was rejected because manual credit notes hold `Reversal of: INV/...` there, and `invoice_origin` is not reliably set on credit notes.

Displaying it needs no new access rule, since many-to-one display names are read with sudo.

### 3. Use a related field for Reversal Of

Add `reversed_entry_id` as an unstored related field to `move_id.reversed_entry_id`. It doesn't need grouping or totals, so it doesn't need a stored column.

### 4. Add a dedicated By Item search view

Add a `mode=primary` search view inheriting `account.view_account_move_line_filter`, set as the action's `search_view_id`, with a priority above core's 16 so it does not become the default elsewhere. It holds the new Invoices, Credit Notes and Reversed filters, an Order search field and an Order group-by.

The existing extension view stays as it is. Moving it would remove the payment status filters from other screens, which is outside this change. The primary view still inherits those filters through the core view.

### 5. Default to core's Posted filter

Set `search_default_posted` in the action context, reusing the core `posted` filter. A filter rather than a domain lets users remove it to see draft and cancelled documents.

### 6. Keep the remaining list columns unchanged

The Invoice column keeps its label and `Reversed` gets an info badge colour. `Invoice Date` continues to show the accounting `date`.

## Edge Cases

- **Partial return:** the deposit credit note holds the proportional amount, so the net is the unreturned part. Several partial credit notes each appear as a line.
- **Held deposits:** released or forfeited holds produce no credit note, so no line appears. The spec records this, and it is in the user documentation so accounting doesn't expect one.
- **Refund not yet paid:** the credit note shows its own status, such as `Not Paid`, so outstanding refunds are visible.
- **Fully credited unpaid invoice:** it becomes `Reversed`. Both documents stay listed and net to zero.
- **Cash-paid invoice with a credit note:** both documents show `Paid` once the refund is registered, and Reversal Of provides the link.
- **Credit note with no original invoice or order:** still listed, with those columns empty.

## Risks / Trade-offs

- **[Stored columns on a core table]** Upgrading computes three new columns across `account_move_line`, including lines the report doesn't show. → Lines without a product have a signed value of 0, the table is small at this site, and the upgrade runs in the usual maintenance window.
- **[Mixed currencies]** Totals add document-currency amounts, as they do today. → No change for the current THB-only deployment. Multi-currency reporting is out of scope.
- **[Totals change for users]** The same data now shows lower net totals, and the default hides draft and cancelled documents. → Cover this in the user documentation and tell accounting at release.
- **[Ungrouped totals cover one page]** Standard Odoo list behaviour, and unchanged by this report: the footer sums the current page or selection, not the whole result. Found during QA, where it showed 70,690.49 for rows 1-80 of 120 against a full net of 527,407.33. → Documented for users. Group rows are totalled by the database and are correct.
- **[Group rows sum Quantity and Unit Price]** Both stay positive, so these sums ignore credit notes and are not meaningful. They already appear when grouping today. Hiding them would mean changing the core fields on every screen, so they are left as they are. → Documented for users.
- **[Saved filters or exports using `tax_amount`]** Removing the field would break a saved export that uses it. → Check for references during QA, and restore the field if one is found.

## Migration Plan

1. Back up the database and upgrade `ggg_rental` (`-u ggg_rental`). The ORM creates and fills the new columns, and no migration script is needed.
2. Confirm totals on a known order, using the manual QA steps in `tasks.md`.
3. **Rollback:** restore the previous module version. The extra columns are harmless and no accounting value has changed, so no data restore is needed.
