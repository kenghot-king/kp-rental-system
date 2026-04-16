## Why

Deposit lines currently inherit price from the rental product's `list_price`, which is the rental sale price — not a meaningful deposit amount. There is no dedicated field to configure per-product deposit prices, and the deposit tax is incorrectly taken from the rental line rather than the deposit product itself.

## What Changes

- Add `deposit_price` field (`Float`, company-dependent) on `product.template`, visible in the rental tab
- Change deposit line price source: `line.product_id.list_price` → `line.product_id.deposit_price`
- Change deposit line tax source: `line.tax_ids` → `deposit_product.taxes_id` (the company's configured rental deposit product's taxes)
- Remove price mismatch check from `_check_deposit_sync()` — price on deposit lines is no longer compared to product price

## Capabilities

### New Capabilities
- `rental-product-deposit-price`: A company-dependent deposit price field on rental products, used to populate deposit line amounts when syncing deposits on rental orders.

### Modified Capabilities

## Impact

- **Models**: `product.template` (new field), `sale.order` (`action_sync_deposits`, `_check_deposit_sync`)
- **Views**: Product form — rental tab (new field)
- **Config**: No new settings — reuses existing `rental_deposit_product_id` from Rental Settings
