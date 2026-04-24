## 1. Shop Card — Deposit & Disabled Checkout

- [x] 1.1 In `views/website_rental_shop_templates.xml`, extend the existing `rental_products_item` override to add a deposit line below the daily rate: "Deposit: ฿{deposit_price}", guarded by `t-if="product.deposit_price"`
- [x] 1.2 Inherit `website_sale.shop_product_buttons` — wrap the button content with `t-if="not product.rent_ok"` to hide Add-to-Cart for rental products

## 2. Product Detail — Typo Fix & i18n

- [x] 2.1 In `views/website_rental_shop_templates.xml`, update the deposit sub-label from hardcoded `ซ้อระ ณ วันรับ` to `(Pay on pick-up day)` as a translatable text node
- [x] 2.2 Create `i18n/th.po` with the Thai translation: `msgid "(Pay on pick-up day)"` → `msgstr "(ซำระ ณ วันรับ)"`
- [x] 2.3 Register `i18n/` in `__manifest__.py` so Odoo loads it (add `'data'` entry is not needed — Odoo auto-loads `i18n/*.po` files from the addon directory)

## 3. Product Detail — Disable Checkout

- [x] 3.1 In `views/website_rental_shop_templates.xml`, inherit `website_sale.product` — add `t-if="not product.rent_ok"` on the CTA section div (`o_wsale_product_details_content_section_cta`) to hide Add-to-Cart/Buy-Now for rental products while keeping the pricing block visible

## 4. Verification

- [x] 4.1 Upgrade `ggg_rental_website` module and load Thai translations
- [x] 4.2 Verify `/shop` card: rental product shows daily rate + deposit; no Add-to-Cart button
- [x] 4.3 Verify `/shop/{product}`: deposit sub-label is "Pay on pick-up day" in English locale; no Add-to-Cart form rendered; rental pricing block still visible
- [x] 4.4 Verify non-rental products are fully unaffected (Add-to-Cart visible, no deposit line)
