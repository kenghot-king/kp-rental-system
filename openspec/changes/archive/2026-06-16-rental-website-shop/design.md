## Context

`ggg_rental` manages rental products, pricing tiers (`product.pricing` via `product_pricing_ids`), and deposits (`deposit_price`) entirely in the backend. The Odoo e-commerce shop (`website_sale`) has no awareness of these fields — it renders standard sale price only.

`ggg_rental` intentionally has no dependency on `website_sale` to keep it deployable on instances without e-commerce. A new addon `ggg_rental_website` bridges the two without coupling them.

**Key data model:**
- `product.template.product_pricing_ids` → One2many to `product.pricing`
- `product.pricing.price` + `recurrence_id.duration` + `recurrence_id.unit` → defines a pricing tier
- `PERIOD_RATIO = {hour: 1, day: 24, week: 168, month: 744}` — used to normalize all periods to hours for comparison
- `product.template.deposit_price` — Float, company-dependent

## Goals / Non-Goals

**Goals:**
- Show cheapest daily rental rate on `/shop` product cards (listing page)
- Show full rental pricing block on `/shop/{product}` detail page
- Highlight the pricing tier with the best (lowest) per-day rate
- Show deposit amount on the detail page
- Keep `ggg_rental` free of any `website_sale` dependency

**Non-Goals:**
- Per-product pickup/return locations (deferred)
- Online rental booking / cart flow
- Date picker or availability check on the shop
- Price filtering or sorting by rental rate

## Decisions

### Decision 1: Separate addon `ggg_rental_website`

**Chosen**: New addon depending on `[ggg_rental, website_sale]`.

**Alternatives considered**:
- Merge into `ggg_rental` with `website_sale` in depends — rejected because it forces e-commerce on every deployment.
- Monkey-patch via a controller only — rejected because computed fields need to be on the model for template access.

### Decision 2: Computed fields on `product.template`

Two computed fields added in `ggg_rental_website`:

| Field | Type | Logic |
|---|---|---|
| `rental_base_daily_price` | Float | `min(price / (duration * PERIOD_RATIO[unit] / 24))` across all `product_pricing_ids` |
| `rental_best_pricing_id` | Many2one → `product.pricing` | the pricing record that yields `rental_base_daily_price` |

Price-per-day formula:
```
price_per_day = rule.price / (rule.recurrence_id.duration
                              * PERIOD_RATIO[rule.recurrence_id.unit] / 24)
```

**Why not store in the database?** These are pure computations from existing data — no `store=True` needed. They compute on the fly from `product_pricing_ids`.

### Decision 3: QWeb template inheritance

Override standard `website_sale` templates via `t-inherit` — Odoo's standard extension mechanism. No controller override needed; the product object is available in the template context.

Templates to inherit:
- `website_sale.products_item` — inject rental rate badge on shop listing card
- `website_sale.product` — inject rental pricing block on product detail page

### Decision 4: Best-value highlight logic

The pricing tier with the lowest computed ฿/day is `rental_best_pricing_id`. In the template, this tier renders with the highlighted style (blue background + "฿X/DAY" badge), matching the design mockup. All other tiers render in plain style.

## Risks / Trade-offs

- **`website_sale` template names may differ across Odoo versions** → Mitigation: verify exact template XML IDs against the installed Odoo 19 CE source before writing `t-inherit`.
- **Computed fields not stored — performance** → For shops with many products, computing per-day rates on every page render could be slow. Mitigation: acceptable at typical catalog sizes; add `store=True` + recompute trigger if profiling shows it as a bottleneck.
- **`product_pricing_ids` empty** → Some rental products may have no pricing rules (only `list_price`). Mitigation: computed fields return `0.0` / `False` when empty; templates guard with `t-if="product.rental_base_daily_price"`.
