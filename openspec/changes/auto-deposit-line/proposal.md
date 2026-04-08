## Why

When a user adds a rental product to a sale order, a corresponding deposit line must be created manually. This is error-prone — staff may forget to add the deposit, use the wrong amount, or fail to keep quantities in sync. Automating deposit line creation ensures every rental order has a correct, consistent deposit that stays synchronized with the rental line.

## What Changes

- Add a `rental_deposit_product_id` (Many2one → `product.product`) field on `res.company` to designate the deposit product per company, selectable from products with `is_rental_deposit=True`.
- Expose this setting in `res.config.settings` under rental configuration.
- When a rental product is added to a sale order line, auto-create a linked deposit line:
  - Product: the company's configured deposit product
  - Name: `[Deposit] {rental product name}`
  - Unit price: rental product's `list_price`
  - Quantity: synced with the rental line's quantity
  - Taxes: copied from the rental product's taxes (not the deposit product's default taxes)
- The deposit line is read-only in the UI (qty, price, product cannot be edited by the user).
- Deposit line quantity auto-updates when the parent rental line quantity changes.
- Deposit line is auto-deleted when the parent rental line is removed.
- If no deposit product is configured on the company, raise a `UserError` when the user tries to add a rental product to the order.
- Add a `deposit_parent_id` (Many2one → `sale.order.line`) on `sale.order.line` to link deposit lines to their parent rental lines.

## Capabilities

### New Capabilities
- `auto-deposit-line`: Automatic creation, sync, and lifecycle management of deposit lines when rental products are added to sale orders.
- `deposit-product-config`: Company-level configuration for the designated rental deposit product.

### Modified Capabilities

## Impact

- **Models**: `res.company`, `res.config.settings`, `sale.order.line`
- **Views**: `res.config.settings` form (new field), `sale.order` form (deposit lines readonly)
- **Existing behavior**: The current manual deposit workflow is replaced by automatic creation. Existing `is_rental_deposit` flag on `product.template` is reused as the domain filter. Downstream invoice splitting and credit note logic (`_create_deposit_credit_note`) should work unchanged since auto-created deposit lines use a product with `is_rental_deposit=True`.
