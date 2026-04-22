## Context

The rental pricing system uses `product.pricing` records (each with a `recurrence_id` carrying `duration` and `unit`) attached to a product. When a rental order line is priced, `product_pricelist._compute_price_rule()` calls `product._get_best_pricing_rule()` which iterates all applicable rules, computes the total cost if that single rule were applied for the full duration (using `ceil`), and returns the cheapest one. The winner is then used exclusively — the entire rental is priced as N repetitions of that one period.

This produces counter-intuitive results when the duration doesn't align with a single period boundary (e.g., 22 days at [12d/500฿, 7d/300฿, 1d/50฿] → picks 12d×2 = 1,000฿ instead of 12d+7d+3d = 950฿).

## Goals / Non-Goals

**Goals:**
- Decompose rental duration greedily: largest period first (`floor`), smallest period last (`ceil` for remainder)
- Produce the minimum-cost combination across multiple period tiers
- Handle missing "daily" gracefully: use `ceil` on the smallest available period for any remainder
- Keep all existing pricing rule configuration — no model or UI changes

**Non-Goals:**
- Optimising globally for the absolute minimum (e.g., trying all combinations) — greedy is sufficient and predictable
- Changing how pricing rules are created, stored, or displayed
- Affecting non-rental product pricing

## Decisions

### D1: Greedy over global optimisation

**Decision:** Use greedy (largest-first) decomposition, not exhaustive search.

**Rationale:** Greedy is O(n) per pricing, deterministic, and matches the mental model users have ("use a weekly rate, then fill the rest with daily"). Exhaustive search over all combinations is overkill for the small number of pricing tiers a product realistically has (typically 2–4).

**Alternative considered:** `min()` over all permutations — rejected as unnecessarily complex with no practical benefit.

### D2: `ceil` on the smallest period for the remainder

**Decision:** Apply `ceil(remainder / smallest_period_days)` for the last (smallest) tier.

**Rationale:** If the remaining days are fewer than the smallest period (e.g., 3 days left, smallest is "Weekly"), charging 1 period is fairer than charging 0. Consistent with how the current single-rule engine uses `ceil`. If the smallest period is "Daily" (1 day), `ceil(3/1) = 3` works naturally.

### D3: Replace `_get_best_pricing_rule` with `_compute_greedy_price`

**Decision:** Add a new method `_compute_greedy_price(start_date, end_date, pricelist, currency)` on `product.template` that returns a total price (float), and update `_compute_price_rule` in `product_pricelist` to call it instead of the current one-rule path.

**Rationale:** The return contract changes fundamentally — from "one rule record" to "a total price". Renaming avoids silent misuse of the old method by callers that expect a single `product.pricing` record.

### D4: Period normalisation via existing `PERIOD_RATIO`

**Decision:** Convert all periods to hours using `PERIOD_RATIO` (already defined in `product_pricing.py`), then derive days as `hours / 24`.

**Rationale:** `PERIOD_RATIO` already handles `hour/day/week/month/year`. No new conversion logic needed.

## Risks / Trade-offs

- **Prices change for existing products** — Any product with multiple pricing tiers will produce different (lower) amounts after the upgrade. Existing draft orders recalculate on save. → Communicate change to staff; consider updating any fixed-price order lines manually if needed.
- **Greedy isn't always globally optimal** — Pathological cases exist (e.g., 6d where 3×2d < 1×7d) but require contrived rule sets. In practice, tiers are designed to reward longer periods with better rates. → Acceptable trade-off; document the behaviour.
- **Month/year periods** — Months have variable day counts. `PERIOD_RATIO` uses 31 days/month (approximation). Greedy with monthly periods on exact-day rentals may round unexpectedly. → Out of scope for this change; monthly periods are not currently configured.

## Migration Plan

1. Deploy code changes and upgrade `ggg_rental` module (`-u ggg_rental`)
2. No database migration required — no schema changes
3. Rollback: revert Python files and re-upgrade
