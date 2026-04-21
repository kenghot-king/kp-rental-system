## Context

Rental orders currently track their lifecycle through `rental_status` (pickup → return → returned) on `sale.order`. This only covers the physical return of items. Invoice payment status and deposit refund status live on separate models (`account.move`) with no aggregated view on the order itself.

The order has `invoice_ids` (O2M to `account.move`) which includes both rental invoices and deposit invoices. Deposit invoices are identified by having invoice lines linked to `is_rental_deposit` products. Deposit credit notes are created via `_create_deposit_credit_note()` on `sale.order.line` and linked through `reversal_move_ids` on the deposit invoice.

## Goals / Non-Goals

**Goals:**
- Single stored field on `sale.order` indicating complete vs incomplete, searchable and filterable.
- Tooltip detail showing breakdown: returned x/y, paid x/y, deposit refunded amt/amt.
- Display in Kanban, List, and Form views for confirmed rental orders.
- Reliable recomputation when underlying data changes.

**Non-Goals:**
- Changing the existing `rental_status` field or its behavior.
- Adding completion tracking at the order line level.
- Auto-completing or auto-closing orders when status becomes complete.
- Tracking partial payment amounts (only invoice-level paid/not-paid counts).

## Decisions

### 1. Stored computed field with explicit recompute triggers

**Choice**: `rental_completion` is `store=True` with `@api.depends` for direct dependencies, plus explicit `_recompute_rental_completion()` calls for deep dependency chains.

**Why**: Searchability requires `store=True`. Direct depends handles `order_line.qty_returned`, `order_line.qty_delivered`. But invoice payment state and deposit credit note changes are 2+ hops away — `@api.depends` can't reliably cross `invoice_ids.payment_state` or `invoice_ids.reversal_move_ids.amount_total`. Instead, we trigger recompute explicitly from the code paths we already control.

**Recompute trigger points:**
- `order_line.qty_returned` / `order_line.qty_delivered` → standard `@api.depends`
- Invoice payment state change → override `account.move._compute_amount()` or hook `write()` on payment_state to trigger SO recompute
- Deposit credit note creation → add recompute call at end of `_create_deposit_credit_note()`

**Alternative considered**: Non-stored field — simpler but not searchable/filterable.

### 2. Separate detail field as computed char

**Choice**: `rental_completion_detail` is a non-stored `compute` char field that builds the tooltip text.

**Why**: This field is only used for display (tooltip). No need to store it — always computed fresh. Keeps storage lean and avoids stale tooltip text.

### 3. Deposit invoice identification via invoice line product

**Choice**: A posted `out_invoice` is a "deposit invoice" if any of its `invoice_line_ids` has `product_id.is_rental_deposit == True`.

**Why**: This matches the existing pattern in `_get_invoiceable_lines()` and `_create_invoice()`. No new flags needed.

### 4. Deposit refund ratio as amount-based

**Choice**: Deposit refund completeness = `sum(reversal credit note amounts) / sum(deposit invoice amounts)`, not count-based.

**Why**: Deposits can be partially refunded (proportional to returned qty). A count-based approach would mark a 50%-refunded deposit as "0/1 refunded" which is misleading. Amount-based shows "5,000/10,000" which is accurate.

### 5. Tooltip via field title attribute

**Choice**: Use the `title` attribute on the badge field element in XML views, bound to `rental_completion_detail`.

**Why**: Native Odoo tooltip — no custom JS widget needed. Works across Kanban, List, and Form. The detail text updates with each recompute.

**Note**: In Kanban view (QWeb template), use `t-att-title` to bind the computed field value.

## Risks / Trade-offs

- **[Stale completion status]** → If an invoice is paid outside normal flow (direct DB update, external payment provider), the stored field won't recompute. Mitigation: the explicit trigger covers all standard Odoo payment flows. Edge cases can use a scheduled action or manual "refresh" if needed later.

- **[Performance on large order sets]** → Recomputing completion for many orders when a batch payment is registered could be slow. Mitigation: the recompute is lightweight (count queries, sum queries on related records). No heavy joins needed.

- **[Deposit edge case: no deposit invoices]** → When no deposit invoices exist, the deposit axis is skipped entirely. The completion status only checks returned + paid. The detail text omits the "Deposit refunded" line. This is correct behavior, not a risk, but worth documenting.
