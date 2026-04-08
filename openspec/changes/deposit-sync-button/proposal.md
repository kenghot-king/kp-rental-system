## Why

The previous auto-deposit approach (onchange-based) was unreliable due to Odoo's virtual NewId records causing duplicate and orphaned deposit lines. A button-driven approach gives the user explicit control over deposit creation while still validating correctness at critical moments (Send, Print, Confirm, Preview).

## What Changes

- Add a **[Sync Deposits]** button above the order lines in the rental order form. Clicking it creates, updates, or removes deposit lines to match the current rental lines.
- Add a **deposit validation check** (`_check_deposit_sync()`) that runs before Send, Print, Confirm, and Preview actions. If deposits are out of sync, a wizard popup warns the user with options to update or continue as-is.
- Deposit line values: product = company's `rental_deposit_product_id`, name = `[Deposit] {product name}`, price = rental product's `list_price` (sale price), qty = rental line qty, taxes = rental line taxes.
- Remove the previous auto-sync logic (onchange, write override) from `auto-deposit-line` change — replaced by this button approach.
- Existing infrastructure reused: `deposit_parent_id` field, `rental_deposit_product_id` company config, readonly deposit line attrs in SO view.

## Capabilities

### New Capabilities
- `sync-deposits-button`: A button on the rental order form that creates/updates/removes deposit lines to match rental lines.
- `deposit-validation-wizard`: A validation check + wizard that intercepts Send, Print, Confirm, and Preview actions when deposit data is out of sync.

### Modified Capabilities

## Impact

- **Models**: `sale.order` (new button action, validation check, action overrides), new wizard model `rental.deposit.sync.wizard`
- **Views**: `sale.order` form (Sync Deposits button above order lines), new wizard form view
- **Existing**: Reuses `deposit_parent_id`, `rental_deposit_product_id`, readonly deposit line attrs from previous change. No changes to invoice splitting or credit note logic.
