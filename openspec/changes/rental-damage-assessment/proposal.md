## Why

When a customer returns a rented product in damaged condition, staff have no way to record the damage or charge a damage fee within the system. The deposit credit note is created automatically on return with full refund — there is no opportunity to withhold or charge for damage. Staff currently handle damage manually outside the system, which is error-prone and leaves no audit trail on serial numbers.

## What Changes

- Add condition assessment (good/damaged) to the return wizard for each item/serial being returned
- When staff marks an item as damaged, they enter a damage fee amount and reason
- A "Damage Fee" service line is added to the sales order (separate from deposit and late fees)
- Damage events are logged against `stock.lot` (serial numbers) via a new `rental.damage.log` model
- Deposit refund continues to work as-is (full proportional refund) — damage is a separate charge
- Partial returns with mixed conditions (some good, some damaged) are fully supported
- Damage fees are not capped — if fee exceeds deposit, customer owes the balance

## Capabilities

### New Capabilities
- `damage-assessment`: Condition assessment in the return wizard with damage fee, reason, and per-serial logging
- `damage-history`: Damage log model on `stock.lot` with history view (smart button) for tracking serial damage across rentals

### Modified Capabilities

## Impact

- **Models**: New `rental.damage.log` model; extended `stock.lot` (one2many to damage log); extended `rental.order.wizard.line` (condition, damage fee, reason fields)
- **Wizard**: Return wizard view updated with condition column and conditional damage fields
- **Sale order line**: Return processing logic extended to create damage fee SO lines
- **Views**: `stock.lot` form gets a smart button for damage history
- **No breaking changes** to existing deposit, late fee, or stock move logic
