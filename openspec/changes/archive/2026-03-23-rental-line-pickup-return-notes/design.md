## Context

The SO line `name` field is a text field set by `_get_sale_order_line_multiline_description_sale()` at line creation, which calls `_get_rental_order_line_description()` to append the rental period. The `name` is a stored field that can be updated after creation.

Invoice lines copy their `name` from `self.name` in `_prepare_invoice_line()`, so any updates to the SO line name before invoicing will automatically appear on the invoice.

The `write()` override on `sale.order.line` already handles pickup/return events (validating pickings, creating return moves). This is the natural place to also update the line description.

## Goals / Non-Goals

**Goals:**
- Show picked-up items/qty in SO line description after pickup
- Show returned items/qty in SO line description after return
- Invoice lines inherit these notes automatically

**Non-Goals:**
- Custom invoice line formatting (rely on SO line name inheritance)
- Separate fields for pickup/return notes (keep it in the `name` text field)

## Decisions

### 1. Update `name` directly in the `write()` override

After the stock operations (pickup validation / return creation), rebuild the rental note portion of the `name` field. This keeps all rental lifecycle logic in one place.

**Why not a computed field?** The `name` field is stored and manually editable. Making it computed would conflict with user edits and the existing `_compute_name` flow.

### 2. Use a helper method `_get_rental_notes()` to build the note text

A dedicated method builds the pickup/return annotation text from `pickedup_lot_ids`, `returned_lot_ids`, `qty_delivered`, and `qty_returned`. This keeps the `write()` method clean and makes the note format easy to adjust.

### 3. Rebuild notes on every pickup/return event (not append)

Rather than appending text each time, rebuild the full note section. This handles edge cases cleanly (e.g., cancel scenarios, corrections) and ensures the note always reflects current state.

The `name` field structure becomes:
```
<product description>
<rental period>
<pickup/return notes>   ← rebuilt each time
```

## Risks / Trade-offs

- **[Risk] User manually edits SO line name** → The rebuild would overwrite custom text added after the rental period. Mitigation: only append/replace the notes portion after the rental period line, preserving everything before it.
- **[Trade-off] Name field gets longer** → Acceptable; this is informational text that customers benefit from seeing.
