## Why

The Odoo e-commerce shop (`/shop`) shows only standard sale pricing for rental products, giving customers no visibility into rental rates, pricing tiers, or deposit requirements. This creates friction — customers must contact staff to understand costs before committing to a rental.

## What Changes

- New Odoo addon `ggg_rental_website` that bridges `ggg_rental` and `website_sale`
- `/shop` product cards show the cheapest daily rental rate for rental products
- `/shop/{product}` detail page shows a full rental pricing block: base daily rate, all pricing tiers (with cheapest-per-day highlighted), and deposit amount
- Two computed fields added to `product.template`: cheapest daily rate and the best pricing rule
- No changes to backend rental logic, pricing rules, or existing views

## Capabilities

### New Capabilities

- `rental-shop-card`: Display cheapest daily rental rate on `/shop` product listing cards for `rent_ok` products
- `rental-shop-product-detail`: Display full rental pricing block on `/shop/{product}` detail pages — base rate, all pricing tiers with best-value highlight, and deposit

### Modified Capabilities

## Impact

- **New addon**: `addons/ggg_rental_website/` — depends on `ggg_rental` and `website_sale`
- **New computed fields** on `product.template`:
  - `rental_base_daily_price` (Float) — cheapest price-per-day across all `product_pricing_ids`
  - `rental_best_pricing_id` (Many2one → `product.pricing`) — pricing rule with lowest ฿/day
- **New QWeb templates** overriding `website_sale` shop listing and product detail templates
- No database migrations, no changes to `ggg_rental` models
