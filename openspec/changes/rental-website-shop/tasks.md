## 1. Addon Scaffold

- [x] 1.1 Create `addons/ggg_rental_website/` directory with `__init__.py` and `__manifest__.py` (depends: `ggg_rental`, `website_sale`)
- [x] 1.2 Create `models/__init__.py` and `controllers/__init__.py` stubs
- [x] 1.3 Add addon to the Odoo server's addons path and verify it installs cleanly

## 2. Computed Fields

- [x] 2.1 Create `models/product_template.py` inheriting `product.template`
- [x] 2.2 Implement `rental_base_daily_price` (Float, compute) — returns `min(price_per_day)` across `product_pricing_ids` using `PERIOD_RATIO` normalization; returns `0.0` if no pricing rules
- [x] 2.3 Implement `rental_best_pricing_id` (Many2one → `product.pricing`, compute) — returns the pricing record whose `price / (duration * PERIOD_RATIO[unit] / 24)` is lowest; returns `False` if no pricing rules
- [x] 2.4 Register both fields in `__manifest__.py` data (not needed — model fields auto-register); verify fields appear on product form in debug mode

## 3. Shop Listing Card (`/shop`)

- [x] 3.1 Identify the correct `website_sale` QWeb template XML ID for the product card (verify against installed Odoo 19 CE source)
- [x] 3.2 Create `views/website_rental_shop_templates.xml` with `t-inherit` on the shop card template
- [x] 3.3 Add rental rate snippet below product name: `฿{rental_base_daily_price} / Day`, guarded by `t-if="product.rental_base_daily_price"`
- [x] 3.4 Add XML file to `__manifest__.py` data list
- [x] 3.5 Verify on `/shop`: rental products show the rate; non-rental products are unchanged

## 4. Product Detail Page (`/shop/{product}`)

- [x] 4.1 Identify the correct `website_sale` QWeb template XML ID for the product detail price block
- [x] 4.2 Add `t-inherit` override for the detail page in the same XML file
- [x] 4.3 Implement "฿{X} / Day" large heading (base daily rate), guarded by `rent_ok` and `rental_base_daily_price`
- [x] 4.4 Implement pricing tiers list — loop over `product_pricing_ids`, render each as "฿{price} / {duration} {unit}"
- [x] 4.5 Highlight `rental_best_pricing_id` tier with distinct background and per-day badge (e.g. "฿83/DAY")
- [x] 4.6 Implement deposit row — show "Deposit ฿{deposit_price} (ซ้อระ ณ วันรับ)" guarded by `deposit_price > 0`
- [x] 4.7 Verify on `/shop/{product}`: all tiers listed, best highlighted, deposit shown/hidden correctly

## 5. Styling

- [x] 5.1 Create `static/src/css/rental_shop.css` (or `scss`) for rental pricing block styles matching the design mockup (highlighted tier: blue background, white text; badge: yellow/orange pill)
- [x] 5.2 Register CSS in `__manifest__.py` under `assets > web.assets_frontend`
- [x] 5.3 Verify visual match against `documents/template/eComm-product.png`
