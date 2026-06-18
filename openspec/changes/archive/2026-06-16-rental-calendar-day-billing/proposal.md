## Why

Rental duration is currently measured by raw 24-hour math: `ceil(total_hours / 24)`. Combined with the `add-default-rental-times` defaults (pickup 09:00, return 23:59), this produces a billing surprise: a rental from Apr 29 09:00 to May 3 23:59 is *displayed* as "4 days and 15 hours" but *priced* as 5 days, because 110.98 hours rounds up.

The business actually counts rental periods like a hotel: nights between pickup and return dates. Apr 29 → May 3 = 4 nights = 4 days. The default 23:59 return time exists precisely so the customer gets the full last calendar day without rolling into a new billable day. The pricing engine needs to honour that convention rather than fight it.

This change switches duration measurement from "raw 24h math" to "calendar-day difference between dates" everywhere — both the price computation and the display fields — so what the customer sees is what they pay.

## What Changes

- `product.pricing._compute_duration_vals()` — change `day` from `ceil(total_hours / 24)` to `(end.date() - start.date()).days`; derive `week` and `month` from days; keep `hour` as raw total
- `sale.order._compute_duration()` — change `duration_days` and `remaining_hours` to match the billing model: when calendar-day diff > 0, show `duration_days = calendar_diff` and `remaining_hours = 0`; when calendar-day diff = 0 (sub-day rental), show `duration_days = 0` and `remaining_hours = ceil(total_hours)`
- Sub-day rentals (same calendar date) — pricing falls through to the hourly tier via the existing greedy algorithm; if no hourly tier exists, apply a minimum 1-day fallback so the order still gets a price
- Update the `phase1-qa-test-cases` change's test expectations that were pinned to the old model
- Update the rental contract Thai template if necessary (currently uses `duration_days` + `remaining_hours` — values change but the template logic should still render correctly)

## Capabilities

### New Capabilities
- `rental-calendar-day-billing`: Calendar-day-difference duration model for rental pricing and display, with sub-day fallback to hourly tier or minimum 1 day

### Modified Capabilities

(none — this replaces an internal computation; no public API or field shape changes)

## Impact

- **Models**: `product.pricing._compute_duration_vals()` and `sale.order._compute_duration()` change semantics; field types and signatures unchanged
- **Pricing**: All rental orders re-compute differently. Existing confirmed orders are unaffected (prices are stored on the order line). Quotations recomputed on next refresh.
- **Display**: Form view and Thai contract printout will show the new day count. No view file changes expected (existing labels still apply).
- **Tests**: `phase1-qa-test-cases/specs/tc-rental-order/spec.md` has scenarios pinned to old values (`duration_days=2, remaining_hours=5` for cases that no longer compute that way) — needs update.
- **Dependencies**: None new
- **Existing data**: Confirmed orders untouched. Draft quotations will recompute on next price refresh — operationally acceptable since draft quotations are by definition not yet committed.
