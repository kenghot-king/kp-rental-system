## 1. Restore Add-to-Cart on Product Detail Page

- [x] 1.1 In `addons/ggg_rental_website/views/website_rental_shop_templates.xml`, remove the entire second `<xpath>` block inside `rental_product_detail` that sets `t-attf-class` with `d-none` on `o_wsale_product_details_content_section_cta` — the CTA section should render normally for all products

## 2. Block Checkout on Cart Page for Rental Items

- [x] 2.1 In `addons/ggg_rental_website/views/website_rental_shop_templates.xml`, add a new template inheriting `website_sale.navigation_buttons` that replaces the `<a role="button" name="website_sale_main_button">` element with a conditional: if any `website_sale_order.website_order_line` has `product_id.rent_ok`, show a disabled button with message "Rental items in cart — contact us to book"; otherwise render the original `<a>` link

## 3. Upgrade & Verify

- [x] 3.1 Upgrade the `ggg_rental_website` module via `docker exec`
- [x] 3.2 Verify `/shop/{product}` for a rental product: Add-to-Cart button is visible and functional, rental pricing block still renders
- [x] 3.3 Add a rental product to cart, then visit `/shop/cart`: "Proceed to Checkout" button is replaced with the disabled rental notice
- [x] 3.4 Verify `/shop/cart` with only non-rental products: standard "Proceed to Checkout" button still renders normally
