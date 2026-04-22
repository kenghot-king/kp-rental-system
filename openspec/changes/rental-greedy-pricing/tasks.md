## 1. product_template.py — replace pricing selection with greedy computation

- [x] 1.1 In `models/product_template.py`, add method `_compute_greedy_price(self, start_date, end_date, pricelist, currency)` that: (a) gets all suitable pricings via `ProductPricing._get_suitable_pricings(product, pricelist)`; (b) builds a list of `(period_in_days, rate_in_currency)` tuples, normalizing each period using `PERIOD_RATIO`; (c) sorts descending by period_in_days; (d) applies greedy floor decomposition for all but the last rule, then ceil for the last rule; (e) returns the accumulated total as a float
- [x] 1.2 Keep `_get_best_pricing_rule()` intact (do not delete it) — it may be called by other parts of the codebase. The new method is additive.

## 2. product_pricelist.py — wire greedy price into _compute_price_rule

- [x] 2.1 In `models/product_pricelist.py`, inside `_compute_price_rule()`, replace the block that calls `product._get_best_pricing_rule()` + `pricing._compute_price(duration, unit)` with a call to `product._compute_greedy_price(start_date, end_date, pricelist=self, currency=currency)`; assign the returned float directly as the product's price result

## 3. Verification

- [ ] 3.1 Restart Odoo and upgrade `ggg_rental`; confirm no import or registry errors in logs
- [ ] 3.2 Create a rental order with [12d @ 500฿, 7d @ 300฿, 1d @ 50฿] and 22-day duration; confirm price = 950฿
- [ ] 3.3 Create a rental order with the same product for 7 days; confirm price = 300฿ (exact weekly boundary)
- [ ] 3.4 Create a rental order with [12d @ 500฿, 7d @ 300฿] (no daily) for 22 days; confirm price = 1,100฿ (1×500 + 2×300)
- [ ] 3.5 Create a rental order with a single [1d @ 50฿] rule for 9 days; confirm price = 450฿
