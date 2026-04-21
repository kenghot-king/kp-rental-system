## Why

Rental operators need a clear, at-a-glance indicator of whether a rental order is fully closed out. Today, `rental_status` only tracks the return lifecycle (pickup → return → returned) but says nothing about invoice payment or deposit refund status. Staff must manually cross-check invoices and credit notes to know if an order is truly complete. A single "Complete / Incomplete" status with drill-down detail eliminates this guesswork.

## What Changes

- Add a stored computed field `rental_completion` (Selection: `complete` / `incomplete`) on `sale.order`, evaluated only for confirmed rental orders (`is_rental_order=True`, `state='sale'`).
- Add a computed char field `rental_completion_detail` providing a human-readable breakdown shown as a tooltip on hover (e.g. "Returned: 3/4 \n Paid: 2/3 \n Deposit refunded: 5,000/10,000").
- Completion requires all three conditions:
  1. **Returned**: `sum(qty_returned) >= sum(qty_delivered)` across rental lines.
  2. **Paid**: All posted `out_invoice` (excluding deposit invoices) have `payment_state == 'paid'`.
  3. **Deposit refunded**: Total refunded deposit amount >= total deposit invoice amount. Skipped if no deposit invoices exist.
- Display the completion badge in Kanban, List, and Form views.
- Support search/filter by completion status.

## Capabilities

### New Capabilities
- `rental-completion`: Computed completion status combining return, payment, and deposit refund tracking with UI display across all rental order views.

### Modified Capabilities
None.

## Impact

- **Models**: `sale.order` (new computed fields + search method), `sale.order.line` (trigger recompute on deposit credit note creation).
- **Views**: `sale_order_views.xml` — Kanban, List, and Form views updated with completion badge + tooltip.
- **Dependencies**: No new module dependencies. Relies on existing `invoice_ids`, `reversal_move_ids`, and `payment_state` from `account` module.
