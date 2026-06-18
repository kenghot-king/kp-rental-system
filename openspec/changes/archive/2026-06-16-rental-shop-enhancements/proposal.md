## Why

Three small but impactful improvements to the rental e-commerce shop built in `rental-website-shop`: the product listing card is missing deposit information, a Thai label contains a typo and is hardcoded (not translatable), and the checkout flow should be blocked until it is properly designed for rental workflows.

## What Changes

- `/shop` product listing cards now also display the deposit amount alongside the daily rate
- The deposit sub-label on the product detail page is corrected ("ซำระ ณ วันรับ") and made translatable via Odoo's standard `_()` mechanism so it respects the visitor's selected language
- Checkout is disabled for rental products — the Add-to-Cart / Buy-Now buttons are hidden for `rent_ok` products, replaced with a "Contact Us" or non-functional placeholder, until a proper rental booking flow is implemented

## Capabilities

### New Capabilities

- `rental-shop-card-deposit`: Show deposit amount on the `/shop` product listing card for rental products

### Modified Capabilities

- `rental-shop-product-detail`: Fix deposit sub-label typo and make it translatable; disable checkout buttons for rental products

## Impact

- `addons/ggg_rental_website/views/website_rental_shop_templates.xml` — extend shop card template and modify product detail template
- `addons/ggg_rental_website/models/product_template.py` — no changes needed (deposit_price already available)
- No new models, no database migrations
