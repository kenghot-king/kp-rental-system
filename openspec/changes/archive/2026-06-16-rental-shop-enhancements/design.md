## Context

Three targeted fixes to `ggg_rental_website` (the addon built in `rental-website-shop`):

1. The `/shop` card currently shows the daily rate but not the deposit — customers need to see both before clicking through.
2. The deposit sub-label on the detail page contains a typo (`ซ้อระ` → `ซำระ`) and the Thai string is hardcoded, so English visitors also see Thai text.
3. The standard Odoo checkout flow (Add-to-Cart → payment) is not suitable for rentals (no date picker, no rental contract, etc.) and must be suppressed until a proper rental booking flow is ready.

All changes are confined to `ggg_rental_website/views/website_rental_shop_templates.xml` plus a new `i18n/th.po` file for the translation.

## Goals / Non-Goals

**Goals:**
- Show deposit on `/shop` listing card (below daily rate, only if deposit_price > 0)
- Fix "ซำระ ณ วันรับ" typo on detail page
- Make the deposit label translatable (English source + Thai translation)
- Hide Add-to-Cart button on `/shop` card for rent_ok products
- Hide Add-to-Cart and Buy-Now buttons on `/shop/{product}` for rent_ok products

**Non-Goals:**
- Building a rental booking/checkout flow
- Replacing checkout with a contact form (out of scope for this change)
- Showing any message where buttons were (just hide them silently for now)

## Decisions

### Decision 1: Deposit on shop card

Extend the existing `rental_products_item` template override in `website_rental_shop_templates.xml` — add deposit line below the daily rate badge:
```
฿41.67 / Day
Deposit: ฿100
```
Guarded by `product.deposit_price` (falsy = 0.0 → not shown).

### Decision 2: i18n for deposit sub-label

**Chosen approach**: Change the hardcoded Thai string in the template to an English source string wrapped in `env._()`, then add a `i18n/th.po` file with the Thai translation.

```xml
<small class="text-muted">(<t t-out="env._('Pay on pick-up day')"/>)</small>
```

`i18n/th.po`:
```
msgid "Pay on pick-up day"
msgstr "ซำระ ณ วันรับ"
```

**Why not just fix the typo in the hardcoded Thai string?** A hardcoded Thai string is always Thai regardless of the visitor's language setting. Wrapping in `env._()` makes Odoo serve the translated string based on the active language — English visitors see "Pay on pick-up day", Thai visitors see "ซำระ ณ วันรับ".

### Decision 3: Disable checkout — shop card

Inherit `website_sale.shop_product_buttons` and wrap the button content with `t-if="not product.rent_ok"`. Rent_ok products get an empty actions container — no button, no replacement text.

### Decision 4: Disable checkout — product detail page

The detail page checkout flow is driven by `_is_add_to_cart_possible()`. The cleanest non-invasive approach: inherit `website_sale.product` and add `t-if="not product.rent_ok"` around the `<form>` block, leaving only the title shown for rent_ok products (no form, no Add-to-Cart).

**Why not override `_is_add_to_cart_possible()`?** That would affect backend logic too. Template-level suppression is reversible and frontend-only.

## Risks / Trade-offs

- **Empty CTA area on card** — hiding the button leaves blank space in the card footer. Acceptable for now; can be styled or filled later.
- **Template fragility** — if Odoo 19 refactors `shop_product_buttons` or the detail form structure, these overrides may need updating. Mitigated by keeping xpath targets as stable as possible (`id` attributes over class-based).
- **`env._()` in QWeb** — `env._()` works in QWeb server-side rendering but requires the translation to be loaded. The `.po` file must be imported after module install.
