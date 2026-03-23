## Why

Rental SO lines and their corresponding invoice lines don't show which items were picked up or returned. For serial-tracked products, there's no record on the document of which serial numbers were involved. For non-tracked products, the pickup/return quantities aren't visible in the line description. This makes SO printouts and invoices less informative for both staff and customers.

## What Changes

- After pickup, append picked-up info to the SO line `name` field:
  - Serial-tracked: "Picked up: SN001, SN002"
  - Non-tracked: "Picked up: 3"
- After return, append returned info to the SO line `name` field:
  - Serial-tracked: "Returned: SN001"
  - Non-tracked: "Returned: 2"
- Invoice lines inherit the SO line name automatically, so pickup/return notes appear on invoices without additional overrides

## Capabilities

### New Capabilities
- `rental-line-notes`: Pickup and return annotations on SO line descriptions, flowing through to invoice lines

### Modified Capabilities

## Impact

- **Models**: `sale.order.line` — update `name` field in `write()` override when pickup/return occurs
- **No new dependencies**
- **Invoice lines**: inherit updated name from SO line via existing `_prepare_invoice_line()` — no changes needed
