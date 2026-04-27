## Context

The rental form already shows availability information via the standard `sale_renting` module: a tooltip on each line displays "Forecasted Stock" and "Available" numbers, with a red icon when the line would overbook. However, this is purely informational. The user can save and confirm regardless. Recent work (Suspend reparenting) has already corrected the underlying availability number — Damage and Inspection units no longer pollute Free to Use at warehouse scope. This change converts that corrected number into an actual gate.

The existing `qty_in_rent` computed field on `product.product` already aggregates currently-out rental units, but it's read-only. Standard Odoo's `free_qty` field on `product.product` provides "currently available, not reserved" at the warehouse scope, which is exactly what we want.

The pattern for "explicit action method on the order" is already established in this codebase by `action_sync_deposits()` on `sale.order`. We follow the same pattern for the availability check.

## Goals / Non-Goals

**Goals:**
- A rental order cannot transition from `draft` to `sale` if any of its rental lines would overbook the corresponding product.
- Operators see the gap live as they edit (onchange warning).
- The error names the product, requested qty, available qty, warehouse, and the next action.
- Service products are exempt.
- Multi-line same-product on a single order is summed before checking.
- Drafts and quotations save without restriction.

**Non-Goals:**
- No `@api.constrains` on save — drafts must remain freely editable for operators iterating on a quotation.
- No "legacy reduce" exception — already-confirmed orders are simply not re-validated; only new confirmations run the check.
- No period-overlap math — the user explicitly chose "available now" semantics.
- No serial-level conflict checks at this layer — the existing pickup wizard's `pickeable_lot_ids` filter handles it at physical pickup.
- No manager override mechanism — the user explicitly chose "no override for now".
- No company-level toggle — single global policy.

## Decisions

### D1. Use `product.free_qty` as the availability source

`product.free_qty` is computed by standard Odoo as `qty_available - reserved_quantity` at the warehouse scope. After the recent Suspend reparenting, it correctly excludes Damage / Inspection / Rental locations. Most accurate available number without writing custom SQL.

**Alternatives considered:**
- `qty_available - qty_in_rent`: less accurate; double-counts pending pickings.
- Custom SQL aggregation across `stock.quant`: redundant — `free_qty` already does this correctly.

### D2. Check via action method, enforced at confirm

Following the `action_sync_deposits` pattern, an explicit method `action_check_rental_availability()` lives on `sale.order` and:
- Iterates the order's rental lines.
- Groups by product and sums `product_uom_qty`.
- For each product (skipping services), reads `free_qty` scoped to the order's warehouse.
- Raises `ValidationError` with a helpful message if any group exceeds availability.
- Returns `True` on success (so it can be chained from buttons or other actions).

The check is invoked from `_action_confirm()` before calling `super()`, ensuring the draft→sale transition is blocked when the order would overbook.

```
   user clicks "Confirm"
        │
        ▼
   _action_confirm()
        │
        ├── action_check_rental_availability()  ──► raise if overbooked
        │
        └── super()._action_confirm()  ──► state moves to 'sale'
```

**Alternatives considered:**
- `@api.constrains` on save: requires `_origin` mechanics that don't work reliably in the constrain context for newly-created records, and over-restricts drafts.
- Override `write()`: more invasive, harder to reason about, fires too often.
- Pure onchange: not authoritative, can be bypassed by direct ORM writes.

### D3. Per-line onchange warning

The onchange fires when the user edits `product_id` or `product_uom_qty` on a single line. It returns Odoo's standard `{'warning': {'title': ..., 'message': ...}}` format if that single line's qty would exceed the product's `free_qty`. It does NOT sum across the order — that's the confirm-time check's job. Onchange is purely a courtesy for fast feedback.

```python
@api.onchange('product_id', 'product_uom_qty')
def _onchange_check_rental_availability(self):
    if not self.is_rental or self.product_id.type == 'service':
        return
    ...
    if self.product_uom_qty > available:
        return {'warning': {...}}
```

### D4. Multi-line same-product summing at confirm

A single order can have multiple lines for the same product (e.g., separate sub-products or pricing tiers). The confirm-time check groups lines by `product_id` within the order and compares the sum to `free_qty`. This catches the case where a user splits qty 5 into two lines of 3 + 2 hoping to slip past the per-line check.

### D5. Skip service products entirely

Service products have `product.type == 'service'` and no meaningful `free_qty`. The check returns early for them. Matches user requirement.

### D6. Single helpful error message format

Used by both the onchange warning and the confirm-time error:

```
   Cannot rent {qty} × {product_name}.

   Requested: {requested_qty}
   Currently available in {warehouse}: {available_qty}

   Reduce the quantity to {available_qty} or add more stock to proceed.
```

A private helper `_get_availability_error_message()` produces the string, called from both layers, ensuring identical wording.

## Risks / Trade-offs

- **[Drafts can be saved with overbooked qty]** → By design. Operators iterate on quotations. The block fires at confirm, not save. The onchange warning provides live feedback during editing.
- **[`free_qty` is per-warehouse; multi-warehouse instances may need scoping]** → Mitigation: query `free_qty` with the order's warehouse in context. Single-warehouse installations work without extra logic.
- **[Race condition: two operators confirming overlapping orders simultaneously]** → If both pass the check (because `free_qty` is read before either commits), one will succeed and the other will succeed too, leading to overbooking. Mitigation: not addressed here. Single-operator instances aren't affected. Multi-operator instances would need transactional locking on `stock.quant` — out of scope.
- **[Already-confirmed orders never re-validated]** → Acceptable: cancelling and re-confirming would re-trigger the check, and direct edits on confirmed orders are rare in normal flow.
- **[Decimal-UOM products]** → Use `float_compare` with the product's UOM rounding to avoid floating-point false positives.

## Migration Plan

1. Deploy code change. No DB schema change, no upgrade required beyond a module reload.
2. Check takes effect at next confirmation.
3. Existing draft/quotation orders that would currently overbook can still be saved as drafts; they just can't be confirmed without fixing.
4. Existing already-confirmed orders are unaffected.
5. Rollback: revert the module — no orphaned data, no migration cleanup needed.

## Open Questions

None — design is clear. Implementation follows.
