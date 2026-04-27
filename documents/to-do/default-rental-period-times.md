# Default Rental Period Start/End Time Configuration

**Status:** Pending
**Raised:** 2026-04-27

## Current focus

Add company-level configuration for default pickup time and default return time on rental orders.

### Proposed configuration

In **Rental → Configuration → Settings**, add a new section:

| Field | Default |
|---|---|
| Default Pickup Time | `09:00` |
| Default Return Time | `23:59` |

Stored as fields on `res.company` (e.g. `default_pickup_time`, `default_return_time`).

### Behavior

When a user sets pickup date and return date on a rental order without specifying time, the configured default time is applied to each.

---

## Parked for later

The following questions came up during discussion but are deferred until the basic configuration above is in place.

### Edge cases for the time defaults

- **Same-day rentals:** Pickup May 1 09:00, period = 1 day → return May 1 23:59 or May 2 23:59?
- **Late-day pickup:** Pickup May 1 22:00, period = 5 days → return May 5 23:59 (calendar) or May 6 22:00 (24h)?
  - Calendar interpretation gives customer "less than full day" on day 1.
- **Sub-day rentals:** For periods < 1 day, the time snap should NOT apply — keep raw datetime math.
- **Per-product override:** Should some products override the company default (e.g. tools rental closes at 17:00 instead of 23:59)?
- **Manual edits:** If user manually edits the time after auto-snap, system must NOT keep re-snapping.
- **Calendar-day mode toggle:** Should there be a flag like "Use calendar days for daily-or-longer rentals" so 24h math and calendar math can coexist?

### Pricing implication (must verify)

```
Pickup May 1 09:00, return May 5 23:59
Raw duration: 4d 14h 59m

Does Odoo's pricing rule lookup use:
  (a) date diff = 4 days × rate    ← what we want
  (b) raw hours rounded up = 5 days × rate    ← over-bills by 1 day
```

If (b), the pricing logic also needs to switch to date-based counting when this feature is enabled. Otherwise customers would be billed for 5 days when they only used 4.

### Day-counting model (confirmed)

Day-span counting (like hotel nights):

```
Pickup May 1, return May 5 by 23:59
├─day1─┼─day2─┼─day3─┼─day4─┤
May 1  May 2  May 3  May 4  May 5
= 4 day-spans = 4 days
```

Formula: `rental_days = (return_date.date - pickup_date.date)`

Return time (23:59) is the deadline on the return day, not part of the day count.

### Late pickup / late return policy

When customer picks up or returns on a different date than quoted, what happens?

Example: Quoted Mar 1–5 (4 days, paid). Customer picks up Mar 2 and returns Mar 6.

Three policy options identified:

| Policy | Behavior | Bill |
|---|---|---|
| A. Strict | Original dates unchanged. Late pickup forfeits days. Return after Mar 5 23:59 = late fee. | 4d rental + 1d late = 5×rate |
| B. Adjust with prompt | At pickup, system asks staff: "Customer is late, shift return date too?" | 4d, no late fee (if shifted) |
| C. Auto-shift | System auto-extends return date by the late-pickup days. | 4d, no late fee |

Inventory side-effect: Policies B and C must check whether the unit has a conflicting booking on the new return date.

Decision needed before implementing.
