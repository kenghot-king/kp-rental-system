## Context

The `ggg_rental` module manages rental orders via `sale.order`. A rental order may contain both rental product lines and a security deposit line. Currently, invoicing creates a single invoice for all lines. When equipment is returned, the deposit should be refunded — but there's no mechanism to issue a credit note for just the deposit portion without manually splitting.

Odoo's `sale.order._create_invoices()` groups lines by keys returned from `_get_invoice_grouping_keys()`. By adding a deposit-aware key, we can split invoices automatically.

## Goals / Non-Goals

**Goals:**
- Split deposit and rental lines into separate invoices automatically
- Auto-generate proportional credit notes on return events
- Keep the UX simple — no extra steps for the user beyond marking a product as deposit

**Non-Goals:**
- Deposit payment workflow (requiring deposit paid before pickup) — future phase
- Partial deposit forfeiture for damage — manual process via existing credit note tools
- Multi-currency deposit handling

## Decisions

### 1. Deposit product flag on `product.template`

Add `is_rental_deposit = fields.Boolean("Is Rental Deposit")` on `product.template`.

**Why**: Simple, explicit. The user marks a product as a deposit product once. All SO lines using that product are treated as deposit lines.

**Alternative considered**: Using a product category or tag — more flexible but adds configuration overhead and ambiguity.

### 2. Invoice split via `_get_invoice_grouping_keys()`

Override `sale.order._get_invoice_grouping_keys()` to include a computed key based on whether the SO line's product is a deposit product.

**Why**: This is Odoo's native mechanism for controlling invoice grouping. It requires no changes to the invoicing wizard or workflow — the split happens transparently.

**Alternative considered**: Post-processing (create one invoice, then split) — fragile, error-prone, fights the framework.

### 3. Auto credit note on return

In `sale.order.line._create_rental_return()`, after the stock move completes, check if there's a linked deposit line on the same SO. If so, create a credit note for the proportional amount.

**Credit amount** = `(qty_returned / qty_delivered) × deposit_invoice_line_amount`

Credit notes are auto-posted (`action_post()` called immediately).

**Why**: Auto-posting avoids orphaned draft credit notes. The user explored manual vs auto and chose auto-posted.

**Alternative considered**: Draft credit notes requiring manual posting — adds friction, risk of forgotten drafts.

### 4. Finding the deposit line

Given a rental SO line being returned, find the deposit line on the same SO:
```python
deposit_line = self.order_id.order_line.filtered(
    lambda l: l.product_id.is_rental_deposit
)
```

If multiple deposit lines exist, each is credited proportionally. If no deposit line exists, no credit note is created.

### 5. Credit note creation

Use `account.move.reversal` wizard programmatically or create the credit note directly via `account.move.create()` with `move_type='out_refund'` referencing the deposit invoice.

**Preferred**: Direct `account.move` creation with `reversed_entry_id` set, for simplicity and control over the credited amount (partial refund, not full reversal).

## Risks / Trade-offs

- **[Partial returns create multiple credit notes]** → Each partial return generates a separate credit note. This is correct accounting but may create many documents. Acceptable for now; consolidation can be added later if needed.
- **[Deposit line without invoice]** → If the deposit hasn't been invoiced yet when return happens, no credit note can be created. Mitigation: skip credit note creation if no posted deposit invoice exists; log a warning.
- **[Multiple deposit products on one SO]** → Each deposit product line gets its own proportional credit. The logic handles this naturally since it iterates deposit lines.
