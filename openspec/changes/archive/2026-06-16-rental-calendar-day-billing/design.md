## Context

Today's duration measurement (`product.pricing._compute_duration_vals`):

```python
duration = end_date - start_date
vals = dict(hour=(duration.days * 24 + duration.seconds / 3600))
vals['day'] = math.ceil(vals['hour'] / 24)
```

For a rental Apr 29 09:00 → May 3 23:59:
- `total_hours` = 110.98
- `day` = `ceil(110.98 / 24)` = `ceil(4.62)` = **5**

But the displayed duration on `sale.order` (`_compute_duration`):
- `duration_days` = `timedelta.days` = **4**
- `remaining_hours` = `ceil(seconds / 3600)` = **15**

Two computations, two answers. The user sees "4 days and 15 hours" and is billed 5 days. The downstream `add-default-rental-times` change (already merged in spirit via commit `beee55f`) defaulted return time to 23:59 specifically so customers wouldn't get charged an extra day for returning on the last calendar day — but the pricing engine never learned that convention.

## Goals / Non-Goals

**Goals:**
- Make the day count match a hotel-style "nights between dates" model
- Make displayed duration and billed duration always equal
- Keep sub-day rentals possible (hourly tier or 1-day fallback)
- Leave week/month/year computation consistent with the new day model

**Non-Goals:**
- Change the greedy pricing algorithm itself (that's `rental-greedy-pricing`'s scope)
- Change the configured default times (that's `add-default-rental-times`'s scope)
- Re-price already-confirmed orders
- Add per-product or per-customer duration policies — one rule for the whole company

## Decisions

### 1. Day count = calendar date difference

```python
days = (end_date.date() - start_date.date()).days
```

| Pickup | Return | Old (`ceil(h/24)`) | New (date diff) |
|---|---|---|---|
| Apr 29 09:00 | May 3 23:59 | 5 | **4** |
| Apr 29 09:00 | May 3 09:00 | 4 | **4** |
| Apr 29 09:00 | Apr 29 17:00 | 1 | **0** (→ hourly path) |
| Apr 29 09:00 | Apr 30 01:00 | 1 | **1** (crosses midnight) |
| Apr 29 09:00 | Apr 30 17:00 | 2 | **1** |
| Apr 29 09:00 | May 6 09:00 | 7 | **7** |

**Why this rule:** It matches how the business already thinks about rentals (nights), and it removes the surprise from the `23:59` default return time. Pickup time and return time become irrelevant for the daily count — only dates matter.

### 2. Display matches billing

`sale.order._compute_duration()` computes:

```python
days = (end.date() - start.date()).days
total_hours = (end - start).total_seconds() / 3600

if days >= 1:
    duration_days = days
    remaining_hours = 0           # absorbed into the day count
else:
    duration_days = 0
    remaining_hours = ceil(total_hours)   # sub-day rental
```

The "and 15 hours" suffix in the form view goes away for any rental ≥ 1 calendar day. For the user's example order: shows **"4 days"** and bills 4 days. No mismatch.

The Thai contract template ([rental_contract_templates.xml:75-83](addons/ggg_rental/report/rental_contract_templates.xml#L75-L83)) already conditionally renders `วัน` and `ชั่วโมง` based on whether each is non-zero — it will render correctly under the new values without template edits.

### 3. Sub-day rentals: hourly tier or 1-day fallback

When `days = 0`, the greedy algorithm falls through to the hourly tier naturally (smallest period last with `ceil`). If the product has no hourly tier configured at all:

```python
# product_template._compute_greedy_price, after the loop:
if total_price == 0 and total_days == 0 and not has_hourly_tier:
    # min-1-day fallback
    total_price = smallest_daily_or_larger_tier.price
```

Concretely: a same-day rental of a product that only has Daily/Weekly/Monthly tiers bills 1 day. This is the conservative business default per the user's choice (i).

**Alternative considered:** Return 0 / refuse to quote. Rejected because it makes the system silently produce broken quotes for products without explicit hourly tiers, which is the common case.

### 4. Week / month / year derivation

```python
vals['week']  = math.ceil(vals['day'] / 7)   if vals['day'] > 0 else 0
vals['month'] = relativedelta-based as today  (calendar month diff, unchanged)
vals['year']  = months / 12                   (unchanged)
```

The week tier still benefits from greedy decomposition when day count is large enough (e.g., 22 days → 3 weeks + 1 day). No change in the algorithm; just feeding it the new `day` value.

### 5. Confirmed orders are not re-priced

Sale order lines store their computed `price_unit` at the time of price calculation. Switching the algorithm will not retroactively re-price confirmed orders. Draft quotations recompute on the next price refresh — that's acceptable since they're not yet committed.

If an operator wants to re-price a draft quotation under the new rule, they click *Update Prices* (existing action) on the order.

## Risks / Trade-offs

- **[16-hour rental that crosses midnight = 1 day]** — Apr 29 09:00 → Apr 30 01:00 (16h, crosses midnight) bills 1 day. Same length rental Apr 29 02:00 → Apr 29 18:00 (16h, same date) bills via hourly tier (or 1-day fallback). This *is* a slight inconsistency — but it matches the hotel model and is acceptable per discussion.

- **[Manual return-time edits]** — If an operator manually sets return time to, say, 02:00 the next day (instead of 23:59), the day count goes up by 1. That's correct under the new model (a different calendar date = an extra day) and matches how staff will reason about it.

- **[QA test cases pinned to old model]** — `phase1-qa-test-cases/specs/tc-rental-order/spec.md` has at least two scenarios with `duration_days=2, remaining_hours=5` style assertions. Need to update those assertions or rewrite the scenarios under the new model. Listed as a task.

- **[Greedy algo with 1-day total + hourly tier]** — Greedy currently sorts largest-first and uses ceil only on the *last* (smallest) tier. If `days = 1` and tiers are [Daily, Hourly], it bills 1 day (daily floor consumes the whole day). The hourly tier never engages. That's actually the correct behaviour under the new model: any rental that touches 2 calendar dates is at least 1 day, period. The hourly tier only ever fires for sub-day rentals (`days = 0`).

## Migration Plan

1. Land code changes in `product.pricing` and `sale.order`
2. Update QA spec assertions
3. Module upgrade — no DB migration; computed fields recompute on next read
4. Notify operators that draft quotations may show different prices on refresh — recommend a one-time manual *Update Prices* on long-lived drafts
