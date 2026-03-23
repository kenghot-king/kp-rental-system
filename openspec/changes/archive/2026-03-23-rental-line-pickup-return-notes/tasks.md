## 1. Core Implementation

- [x] 1.1 Implement `_get_rental_notes()` on `sale.order.line` — returns pickup/return note text based on current `pickedup_lot_ids`, `returned_lot_ids`, `qty_delivered`, `qty_returned`, and `tracking`
- [x] 1.2 Implement `_update_rental_notes()` on `sale.order.line` — rebuilds the `name` field by stripping old notes and appending fresh output from `_get_rental_notes()`
- [x] 1.3 Call `_update_rental_notes()` in the `write()` override after pickup (qty_delivered change) and return (qty_returned change)

## 2. Verification

- [x] 2.1 Test: Pickup serial-tracked product → SO line name includes "Picked up: SN001, SN002"
- [x] 2.2 Test: Pickup non-tracked product → SO line name includes "Picked up: 3"
- [x] 2.3 Test: Partial return → SO line name includes "Returned: 2"
- [x] 2.4 Test: Multiple returns rebuild notes (not duplicate lines)
- [x] 2.5 Test: Invoice created after pickup → invoice line description includes pickup note
