## Context

The `ggg_rental_website` addon currently hides the entire CTA section (`o_wsale_product_details_content_section_cta`) on `/shop/{product}` with `d-none` for rental products. This prevents JS errors from missing DOM elements, but it also prevents customers from adding items to the cart. The correct UX is: allow cart-add, but block payment checkout when rental items are in the cart.

The cart page (`/shop/cart`) is rendered by `website_sale.cart`. The "Proceed to Checkout" button lives inside a `div.oe_website_sale` form. We can override that template to conditionally replace the button for carts with rental items.

## Goals / Non-Goals

**Goals:**
- Restore the Add-to-Cart button on `/shop/{product}` for rental products.
- Disable the "Proceed to Checkout" button on `/shop/cart` when any cart line contains a rental product.
- Show a clear message explaining why checkout is blocked.

**Non-Goals:**
- Implementing an actual rental booking flow.
- Blocking non-rental products in the same cart.
- Modifying backend order logic or payment providers.

## Decisions

### D1: Remove CTA `d-none` override instead of toggling visibility

The existing `t-attf-class` override on `o_wsale_product_details_content_section_cta` was added to keep DOM elements for JS. Now that we want to restore the CTA, simply remove that xpath block from the template. The JS error concern is resolved because the CTA section will be present normally.

### D2: Detect rental items in cart via QWeb `t-foreach` on `website_sale_order`

Odoo's cart template exposes `website_sale_order.order_line`. We iterate lines and set a flag `has_rental` if any `order_line.product_id.rent_ok`. No controller or Python extension needed — pure QWeb.

### D3: Replace checkout button with disabled notice, not hide it

Hiding the button entirely is confusing. Instead, replace it with a visually disabled button + explanatory text: "Rental items in cart — please contact us to complete your booking." This is more discoverable than a missing button.

### D4: Target `website_sale.cart` checkout button via xpath on `a` with `t-if`

The standard checkout link in `website_sale.cart` is an `<a>` element with class `btn` inside `div.oe_cart`. We use `position="replace"` to swap in a conditional: if `has_rental`, show disabled button; else, show original link.

## Risks / Trade-offs

- [Risk] Odoo 19 cart template structure may differ from assumed xpath → Mitigation: Read actual template source before writing xpath.
- [Risk] `has_rental` flag computed in QWeb may be verbose → Mitigation: Use `t-set` with a filter expression; acceptable complexity for a view-only check.
- [Risk] Customer adds rental + non-rental items together → checkout blocked for all → Trade-off: acceptable for now; mixed carts are an edge case to handle in a future rental booking flow.
