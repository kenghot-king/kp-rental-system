## Context

Rental orders in `ggg_rental` override `_create_invoices()` on `sale.order` to split deposit and non-deposit lines into separate invoices. Standard Odoo creates all invoices as drafts (`state = 'draft'`). The pickup payment gate (`action_open_pickup`) filters for `state == 'posted'` invoices — so draft invoices are invisible to it, causing a false "no invoice issued" error.

The `is_rental_order` Boolean on `sale.order` (computed, stored) is the canonical flag that identifies orders created through the rental app. Deposit invoice lines trace back to the same rental order via `invoice_line_ids → sale_line_ids → order_id`.

## Goals / Non-Goals

**Goals:**
- Auto-post invoices created from rental orders immediately after `_create_invoices()` returns
- Cover both rental invoices and deposit invoices (both trace to `is_rental_order=True`)
- Scope strictly to rental orders — regular sale order invoices are unaffected
- Company-level toggle with default `True`

**Non-Goals:**
- Auto-posting invoices created outside of `_create_invoices()` (e.g. manual invoices)
- Modifying the payment gate logic itself
- Any change to invoice creation for non-rental sale orders

## Decisions

**Scoping: filter invoices by tracing to rental order, not by invoice type**

After `super()._create_invoices()` returns a recordset of new invoices, identify which ones came from rental orders by following: `invoice.invoice_line_ids → sale_line_ids → order_id → is_rental_order`. Post only those.

Alternative considered: guard at the top with `if not self.filtered('is_rental_order'): return`. Rejected — `self` may contain a mix of rental and non-rental orders in a batch invoicing scenario, which would either skip auto-posting entirely or over-post.

**Hook point: `_create_invoices()` override on `sale.order`**

This is the single method already overridden in `ggg_rental` for deposit splitting. Adding the auto-post here ensures all rental invoice creation paths (single, batch, deposit split) are covered without duplicating logic across wizards or controllers.

**Default: `True`**

The setting defaults to enabled because the primary use case (rental with payment gate) requires it, and manually confirming every invoice adds friction with no benefit for most rental workflows.

## Risks / Trade-offs

- [Risk] `action_post()` raises if an invoice has validation errors (e.g. missing journal, missing account). → Mitigation: wrap in `try/except` and log a warning rather than blocking invoice creation; staff can confirm manually.
- [Risk] Auto-posting locks the invoice immediately — staff cannot edit it. → Acceptable: rental invoices generated from confirmed SO lines should not need editing. Manual invoices are unaffected.
- [Risk] Batch invoicing across rental + non-rental orders — only rental-origin invoices are posted. Non-rental invoices remain draft. → Correct behaviour by design.
