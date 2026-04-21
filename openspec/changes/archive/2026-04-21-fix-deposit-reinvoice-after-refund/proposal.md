## Why

When a rental return is processed and the deposit credit note is auto-created, the credit note is linked to the deposit sale order line via `sale_line_ids`. This causes Odoo to recalculate the deposit line's `qty_invoiced` back to zero, making it appear invoiceable again. The next time invoices are created (e.g., for a late-return fee), the deposit split logic picks up the "re-invoiceable" deposit line and creates a duplicate deposit invoice.

## What Changes

- Override `_get_invoiceable_lines()` on `sale.order` to exclude deposit lines that already have at least one posted `out_invoice` linked to them — regardless of the split context (`_rental_deposit_only`, default, etc.)
- Update the `needs_split` check inside `_create_invoices()` to also skip deposit lines that are already invoiced, so the split path is not triggered unnecessarily

## Capabilities

### New Capabilities
- `deposit-invoice-guard`: Prevents duplicate deposit invoicing by excluding already-invoiced deposit lines from the invoiceable line set

### Modified Capabilities
<!-- No existing spec-level requirement changes -->

## Impact

- `addons/ggg_rental/models/sale_order.py` — `_get_invoiceable_lines()` and the `needs_split` check in `_create_invoices()`
- No database migration required (no new fields)
- No impact on credit note creation, deposit refund, or payment flows
