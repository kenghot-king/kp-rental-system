## Context

In Odoo, `sale.order.line.qty_invoiced` is recalculated as:
`sum(out_invoice quantities) - sum(out_refund quantities)` across all `invoice_lines` linked to the SO line.

When `_create_deposit_credit_note()` creates the deposit refund, it links the credit note line to the deposit SO line via `sale_line_ids`. This causes `qty_invoiced` to drop back to zero and `qty_to_invoice` to become 1 again. On the next `_create_invoices()` call (e.g., for a late-return fee), the split logic sees a deposit line with `qty_to_invoice > 0` and creates another deposit invoice.

Current flow in `_create_invoices()`:
1. **needs_split check** — scans `order_line` for lines with `qty_to_invoice > 0`; if both deposit and non-deposit found → split
2. **split path** — calls `super()._create_invoices()` twice: once with `_rental_exclude_deposit`, once with `_rental_deposit_only`
3. **`_get_invoiceable_lines()`** — filters lines for actual invoice creation (called by Odoo core)

The bug manifests because the needs_split check and the `_rental_deposit_only` path both pick up the already-invoiced deposit line.

## Goals / Non-Goals

**Goals:**
- Prevent duplicate deposit invoices after the deposit credit note has been issued
- Fix applies for full return (100% credit) and partial return (partial credit) scenarios
- Keep the credit note linked to the sale line (traceability intact)

**Non-Goals:**
- Change how the credit note is created or linked
- Handle cancellation of the original deposit invoice (edge case; out of scope)
- Modify deposit refund payment or auto-pay logic

## Decisions

### Decision 1: Filter at `_get_invoiceable_lines()` (Direction 1)

Override `_get_invoiceable_lines()` in `sale.order` to exclude deposit lines that already have at least one posted `out_invoice` on `invoice_lines`.

**Why over Direction 2 (remove `sale_line_ids` from credit note):**
- Keeps the credit note visible in the order's Invoices smart button
- `qty_to_invoice` will technically still be > 0 (reflects accounting reality: deposited amount is "back in play"), but we deliberately suppress re-invoicing at the business rule level
- Direction 2 breaks `sale.order.invoice_ids` computation, hiding the RINV from the order view

**Check used:**
```python
already_invoiced = bool(line.invoice_lines.filtered(
    lambda il: il.move_id.state == 'posted' and il.move_id.move_type == 'out_invoice'
))
```
If `True`, the line is excluded from invoiceable lines.

This filter is applied in ALL contexts where deposit lines can appear:
- Default (no context flag): base pass-through
- `_rental_deposit_only`: explicitly skip already-invoiced deposits
- `_rental_exclude_deposit`: already excluded by product filter, no change needed

### Decision 2: Also fix the `needs_split` check

The `needs_split` check in `_create_invoices()` currently scans `order_line.filtered(qty_to_invoice > 0)` directly, bypassing `_get_invoiceable_lines()`. We update the check to also require that the deposit line has NOT been previously invoiced, matching the behavior of `_get_invoiceable_lines()`.

**Why:** Avoids entering the split path unnecessarily, which would call `super()._create_invoices()` with `_rental_deposit_only` and produce an empty recordset. While harmless, it's confusing and slightly wasteful.

## Risks / Trade-offs

- **Risk: Cancelled deposit invoice reopens the deposit** → If the original deposit invoice is cancelled (moved to `cancel` state), `already_invoiced` returns `False`, and the deposit line becomes invoiceable again. This is the correct behavior — a cancelled invoice means the customer was never actually charged.
- **Risk: Multi-company or multi-order batching** → The filter checks `invoice_lines` per line, which works correctly across batched invoice creation (Odoo groups by partner/currency).
- **Trade-off: `qty_to_invoice` stays > 0** → The deposit SO line will show `qty_to_invoice = 1` in technical views even after the credit note. This is a cosmetic inconsistency but does not affect invoicing behavior with this fix in place.

## Migration Plan

No database changes. Deploy by restarting the Odoo service; the fix takes effect on the next invoice creation.
