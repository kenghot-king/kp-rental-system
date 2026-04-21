## Why

Rental return moves created by `_create_rental_return()` are bare `stock.move` records with no `picking_id` and no `origin`. They are invisible in the Inventory → Transfers view and carry no traceability back to the sale order. Warehouse staff cannot audit which SO triggered a stock movement without querying raw move history.

## What Changes

- `_create_rental_return()` in `sale_order_line.py` no longer creates and validates a standalone `stock.move`; instead it creates a `stock.move` under a pre-created `stock.picking` and skips immediate validation
- `RentalOrderWizardLine._apply()` in `rental_processing.py` orchestrates picking creation: one `stock.picking` per unique destination location per return event, grouped before line processing, validated after all moves are added
- Every return picking uses the warehouse `Receipts` operation type (`in_type_id`, WH/IN sequence), `origin = SO name`, and `location_id = rental_loc`
- Applies to all three return destinations: WH/Stock (good condition), WH/Damage (damaged), WH/Inspection (inspect)

## Capabilities

### New Capabilities
- `rental-return-picking`: Proper stock.picking created for every rental return, grouped by destination, stamped with SO number as Source Document

### Modified Capabilities

## Impact

- `addons/ggg_rental/wizard/rental_processing.py` — `RentalOrderWizardLine._apply()` gains pre/post-pass picking orchestration
- `addons/ggg_rental/models/sale_order_line.py` — `_create_rental_return()` accepts optional `picking` parameter; when provided attaches move to it and skips `_action_done()`; existing callers unaffected (backward-compatible default)
- No model changes, no migration required
- Existing delivery pickings (pickup side) are unaffected
