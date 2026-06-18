## Why

The current rental pricing engine picks the single cheapest rule for the entire duration, which means customers are charged for full extra periods when their rental spans between defined intervals (e.g., 22 days = 2× "12 Days" @ 1,000฿ instead of 1×12d + 1×7d + 3×daily = 950฿). A greedy decomposition approach that fills the rental duration with the largest applicable periods first produces fairer, lower prices that match customer expectations.

## What Changes

- Replace the "pick cheapest single rule" algorithm with a **greedy period decomposition** algorithm
- For a given rental duration, the system now decomposes it greedily: largest period first (using `floor`), down to the smallest period (using `ceil` to cover any remainder)
- The total price is the **sum** across all contributing periods, not the cost of a single repeated rule
- No UI changes — pricing rules are configured identically; only the computation changes

## Capabilities

### New Capabilities

- `greedy-rental-pricing`: Greedy decomposition of rental duration across multiple pricing periods, producing the minimum-cost combination by applying larger periods first and using the smallest available period (with ceiling) for any remainder

### Modified Capabilities

## Impact

- `addons/ggg_rental/models/product_template.py` — `_get_best_pricing_rule()` replaced by `_compute_greedy_price()`
- `addons/ggg_rental/models/product_pricelist.py` — `_compute_price_rule()` updated to call the new method and use the returned total price directly
- `addons/ggg_rental/models/product_pricing.py` — `PERIOD_RATIO` used for period normalization (no changes needed)
- No database migrations, no new models, no API changes
