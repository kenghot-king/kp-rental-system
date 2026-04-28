## 1. Pricing Duration Computation

- [x] 1.1 Modify `product.pricing._compute_duration_vals()` in `addons/ggg_rental/models/product_pricing.py` so `vals['day'] = (end_date.date() - start_date.date()).days`
- [x] 1.2 Derive `vals['week'] = ceil(vals['day'] / 7) if vals['day'] > 0 else 0`
- [x] 1.3 Keep `vals['hour']` as raw `total_seconds / 3600` (unchanged)
- [x] 1.4 Keep `vals['month']` and `vals['year']` based on `relativedelta` (unchanged)

## 2. Display Field Computation

- [x] 2.1 Modify `sale.order._compute_duration()` in `addons/ggg_rental/models/sale_order.py`:
  - When `(end.date() - start.date()).days >= 1`: `duration_days = that diff`, `remaining_hours = 0`
  - When `(end.date() - start.date()).days == 0`: `duration_days = 0`, `remaining_hours = ceil(total_seconds / 3600)`
- [x] 2.2 Verify form view ([sale_order_views.xml:54-62](addons/ggg_rental/views/sale_order_views.xml#L54-L62)) renders correctly under all three cases (multi-day, sub-day, zero)
- [x] 2.3 Verify Thai contract template ([rental_contract_templates.xml:75-83](addons/ggg_rental/report/rental_contract_templates.xml#L75-L83)) renders correctly under all three cases

## 3. Sub-day Fallback

- [x] 3.1 In `product.template._compute_greedy_price()`, after the tier loop, add a guard: if `total_days == 0` and no hourly tier exists in `tiers` (smallest tier `period_in_days >= 1`), bill the smallest available tier's rate (1-day fallback)
- [x] 3.2 Add a unit test for: same-day rental, daily-only product → bills 1 day
- [x] 3.3 Add a unit test for: same-day rental, hourly-tier product → bills the configured hourly tier

## 4. Update Pinned QA Test Cases

- [x] 4.1 Read `openspec/changes/phase1-qa-test-cases/specs/tc-rental-order/spec.md` and identify all scenarios that pin `duration_days` / `remaining_hours` to specific values
- [x] 4.2 Update each pinned scenario to reflect the new model (e.g., a 2-day-5-hour rental that previously asserted `duration_days=2, remaining_hours=5` now asserts `duration_days=2, remaining_hours=0` if it crosses midnight twice, or `duration_days=3, remaining_hours=0` if its return is on day 4)
- [x] 4.3 Update `documents/QA/all-testcases/tc-rental-order.md` and `documents/QA/phase1/tc-rental-order.md` to match
- [x] 4.4 Update `documents/brd/brd-odoo-mcp.md` if relevant scenarios reference the old expectations

## 5. Validation

- [x] 5.1 Reproduce the original issue: order Apr 29 09:00 → May 3 23:59 with daily-tier-only product → verify priced at 4 days (not 5)
- [x] 5.2 Verify form view shows "4 days" (no "and X hours" suffix)
- [x] 5.3 Verify Thai contract printout shows the same value
- [x] 5.4 Test sub-day rental with hourly tier → bills configured hourly tier
- [x] 5.5 Test sub-day rental without hourly tier → bills 1 day
- [x] 5.6 Test multi-week rental (e.g., 22 days) with weekly + daily tiers → greedy decomposition still produces the expected combined price under the new day count
- [x] 5.7 Confirm that confirmed (non-draft) orders are not re-priced on module upgrade
