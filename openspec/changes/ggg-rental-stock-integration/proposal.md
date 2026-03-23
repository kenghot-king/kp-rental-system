## Why

The ggg_rental module currently tracks pickup/return quantities on sale order lines (`qty_delivered`, `qty_returned`) but does not create any stock moves. This means inventory levels are never affected by rental operations — products picked up by customers don't reduce stock, and returned products don't increase it. This makes the Inventory module's On Hand / Free to Use quantities unreliable for rental products.

## What Changes

- Add `sale_stock` to ggg_rental's dependencies (brings in stock picking integration for sale orders)
- Override the pickup wizard to validate the delivery picking (moves stock out of warehouse)
- Override the return wizard to create a return picking (moves stock back into warehouse)
- Handle partial pickup/return quantities (e.g., pick up 2 of 3 ordered, return 1 of 2 picked up)
- Ensure rental product reservations are reflected in "Free to Use" vs "On Hand" quantities
- Add stock-related fields and smart buttons to rental order views where needed

## Capabilities

### New Capabilities
- `rental-stock-moves`: Stock picking creation and validation tied to rental pickup/return wizard operations. Covers delivery picking on pickup, return picking on return, partial quantity handling, and stock reservation visibility.

### Modified Capabilities

## Impact

- **Dependencies**: `ggg_rental.__manifest__.py` gains `sale_stock` dependency (which pulls in `stock`)
- **Models**: `sale.order` and `sale.order.line` gain stock-aware overrides; `rental.order.wizard` and `rental.order.wizard.line` gain picking integration
- **Views**: Rental order form may need delivery/return picking smart buttons
- **Existing behavior**: SO confirmation will now auto-create delivery pickings for rental orders (standard `sale_stock` behavior), which changes the current flow where no pickings exist
