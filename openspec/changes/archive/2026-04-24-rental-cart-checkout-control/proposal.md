## Why

The previous change hid the Add-to-Cart CTA entirely on `/shop/{product}` for rental products, but customers still need to add rental items to their cart — the restriction should be at checkout, not at cart-add. Blocking checkout at the cart page keeps the standard e-commerce browsing flow intact while preventing incomplete rental orders from reaching payment.

## What Changes

- **Restore Add-to-Cart on `/shop/{product}`**: Remove the `d-none` hide on the CTA section for rental products so the "Add to Cart" button renders normally.
- **Disable Checkout on `/shop/cart`**: When the cart contains at least one rental product (`rent_ok = True`), the "Proceed to Checkout" button on the cart page is replaced with a disabled notice explaining that rental orders must be completed via the rental booking flow.

## Capabilities

### New Capabilities
- `rental-cart-add`: Rental products can be added to the website cart from the product detail page (CTA section restored).
- `rental-checkout-block`: The checkout button on `/shop/cart` is disabled/replaced when the cart contains rental products.

### Modified Capabilities
- `rental-shop-product-detail`: CTA section is no longer hidden — requirement changes from "hide checkout" to "allow cart add, block only at checkout stage".

## Impact

- `addons/ggg_rental_website/views/website_rental_shop_templates.xml`: Remove the CTA `d-none` override; add new cart-page template override.
- `addons/ggg_rental_website/` (possibly): May need a controller or JS to detect rental items in cart on the cart page.
- No changes to `ggg_rental` models or backend.
