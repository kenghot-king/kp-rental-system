# Test Cases: Pricing & Duration Calculation

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Rental product with `rent_ok=True`
- Multiple pricing rules configured (hourly, daily, weekly, monthly)
- Pricelist configured (optional)

---

## 1. Basic Pricing Rule Setup

### TC-PR-001: Create daily pricing rule

| Field | Value |
|-------|-------|
| **Precondition** | Rental product exists |
| **Steps** | 1. Open product > Pricing tab<br>2. Add rule: recurrence = "Day", price = 500<br>3. Save |
| **Expected** | Pricing rule saved; displayed as "500 / Day" |
| **Result** | |

### TC-PR-002: Create hourly pricing rule

| Field | Value |
|-------|-------|
| **Precondition** | Rental product exists |
| **Steps** | 1. Add pricing rule: recurrence = "Hour", price = 100<br>2. Save |
| **Expected** | Pricing rule saved and visible |
| **Result** | |

### TC-PR-003: Create weekly pricing rule

| Field | Value |
|-------|-------|
| **Precondition** | Rental product exists |
| **Steps** | 1. Add pricing rule: recurrence = "Week", price = 3000<br>2. Save |
| **Expected** | Pricing rule saved |
| **Result** | |

### TC-PR-004: Pricelist-specific rule takes priority over general rule

| Field | Value |
|-------|-------|
| **Precondition** | Product has general daily rule (500/day) and pricelist-specific daily rule (400/day) |
| **Steps** | 1. Create order with pricelist that has the specific rule<br>2. Add product line |
| **Expected** | Price = 400/day (pricelist rule used); not 500/day |
| **Result** | |

### TC-PR-005: Duplicate pricing rule rejected

| Field | Value |
|-------|-------|
| **Precondition** | Product already has a daily rule with no pricelist |
| **Steps** | 1. Try to add another daily rule with no pricelist for same product<br>2. Save |
| **Expected** | Validation error: duplicate pricing parameters |
| **Result** | |

---

## 2. Duration-based Price Calculation

### TC-PR-006: 2-day rental uses daily price × 2

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily price = 500 |
| **Steps** | 1. Create order, start = 2026-05-01 09:00, return = 2026-05-03 09:00<br>2. Add product line, qty = 1 |
| **Expected** | Line price = 1,000 (500 × 2) |
| **Result** | |

### TC-PR-007: 7-day rental uses weekly rule if cheaper

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily = 500/day and weekly = 3,000/week |
| **Steps** | 1. Create order for exactly 7 days<br>2. Check which pricing rule applies |
| **Expected** | Weekly rule used (3,000 < 3,500); price = 3,000 |
| **Result** | |

### TC-PR-008: Partial period rounded up with ceiling

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily price = 500 |
| **Steps** | 1. Create order: start = 2026-05-01 09:00, return = 2026-05-02 12:00 (1.125 days) |
| **Expected** | Price = 1,000 (ceil(1.125 days) = 2 × 500) |
| **Result** | |

### TC-PR-009: Hourly rental — 2.5 hours rounded to 3 hours

| Field | Value |
|-------|-------|
| **Precondition** | Product with hourly price = 100 |
| **Steps** | 1. Create order for 2.5 hours |
| **Expected** | Price = 300 (ceil(2.5) × 100) |
| **Result** | |

### TC-PR-010: Quantity multiplier applied to rental price

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily price = 500 |
| **Steps** | 1. Create order for 2 days<br>2. Set qty = 3 on line |
| **Expected** | Line subtotal = 3,000 (500 × 2 days × 3 qty) |
| **Result** | |

---

## 3. Greedy Pricing (Decomposition)

### TC-PR-011: Greedy — 9 days decomposed to 1 week + 2 days

| Field | Value |
|-------|-------|
| **Precondition** | Product with weekly = 3,000 and daily = 500; greedy pricing enabled |
| **Steps** | 1. Create order for 9 days |
| **Expected** | Price = 3,000 (1 week) + 1,000 (2 days) = 4,000 |
| **Result** | |

### TC-PR-012: Greedy — 30 days uses monthly rule

| Field | Value |
|-------|-------|
| **Precondition** | Product with monthly = 12,000, weekly = 3,000, daily = 500 |
| **Steps** | 1. Create order for 30 days |
| **Expected** | Greedy picks 1 month = 12,000 (cheaper than 4w+2d = 13,000) |
| **Result** | |

### TC-PR-013: Greedy — last tier uses ceiling

| Field | Value |
|-------|-------|
| **Precondition** | Product with weekly = 3,000 and daily = 500 |
| **Steps** | 1. Create order for 10 days (1 week + 3 days) |
| **Expected** | Price = 3,000 + 1,500 = 4,500 |
| **Result** | |

---

## 4. Overnight / Nightly Pricing

### TC-PR-014: Create nightly pricing rule

| Field | Value |
|-------|-------|
| **Precondition** | Rental product exists |
| **Steps** | 1. Add pricing rule with `displayed_unit = night`<br>2. Set price = 800<br>3. Save |
| **Expected** | Rule shows "Night"; `overnight=True`; `unit=hour`, `duration=24` internally |
| **Result** | |

### TC-PR-015: Nightly rules cannot mix with non-nightly rules on same product

| Field | Value |
|-------|-------|
| **Precondition** | Product already has a nightly rule |
| **Steps** | 1. Try to add a daily (non-overnight) rule to same product |
| **Expected** | Validation error: cannot mix overnight and non-overnight |
| **Result** | |

### TC-PR-016: Nightly pricing uses pickup_time and return_time for correct night count

| Field | Value |
|-------|-------|
| **Precondition** | Recurrence: overnight, pickup_time=15:00, return_time=11:00 |
| **Steps** | 1. Create order: pickup 2026-05-01 15:00, return 2026-05-03 11:00 |
| **Expected** | 2 nights counted; price = 2 × 800 = 1,600 |
| **Result** | |

---

## 5. Temporal Recurrence Configuration

### TC-PR-017: Recurrence unit labels — singular vs plural

| Field | Value |
|-------|-------|
| **Precondition** | Recurrences for hour, day, week, month, year |
| **Steps** | 1. Check display labels for each |
| **Expected** | Duration=1 → "Hour/Day/Week/Month/Year"; duration>1 → "Hours/Days/…" |
| **Result** | |

### TC-PR-018: Duration 0 means fixed price (no unit)

| Field | Value |
|-------|-------|
| **Precondition** | Recurrence with duration=0 |
| **Steps** | 1. Check pricing display for product with duration=0 rule |
| **Expected** | Price shown as fixed; no unit multiplier applied |
| **Result** | |

### TC-PR-019: pickup_time validation — must be 0–24

| Field | Value |
|-------|-------|
| **Precondition** | Overnight recurrence record |
| **Steps** | 1. Set pickup_time = 25<br>2. Save |
| **Expected** | Validation error: value must be between 0 and 24 |
| **Result** | |

---

## 6. Variant-Specific Pricing

### TC-PR-020: Pricing restricted to specific variant

| Field | Value |
|-------|-------|
| **Precondition** | Product with variants A and B; pricing rule with `product_variant_ids = [A]` |
| **Steps** | 1. Create order with variant A |
| **Expected** | Restricted pricing rule applied |
| **Result** | |

### TC-PR-021: Pricing with no variant restriction applies to all variants

| Field | Value |
|-------|-------|
| **Precondition** | Pricing rule with empty `product_variant_ids` |
| **Steps** | 1. Create order with variant B (different from TC-PR-020) |
| **Expected** | General pricing rule applied |
| **Result** | |

---

## 7. Display Price on Product Form

### TC-PR-022: Product form shows first pricing rule as display price

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily price = 500 |
| **Steps** | 1. Open product form |
| **Expected** | `display_price` shows "500 / Day" (or formatted equivalent) |
| **Result** | |

### TC-PR-023: SAP article code uniqueness enforced

| Field | Value |
|-------|-------|
| **Precondition** | Product A has `sap_article_code = "ART001"` |
| **Steps** | 1. Try to set `sap_article_code = "ART001"` on a different product<br>2. Save |
| **Expected** | Database/validation error: SAP code must be unique |
| **Result** | |

---

## 8. Currency Conversion

### TC-PR-024: Price converted correctly when pricelist uses different currency

| Field | Value |
|-------|-------|
| **Precondition** | Product price in THB; order uses USD pricelist |
| **Steps** | 1. Create order with USD pricelist<br>2. Add rental product |
| **Expected** | Price shown in USD using current exchange rate |
| **Result** | |

### TC-PR-025: Greedy pricing converts currency at each tier

| Field | Value |
|-------|-------|
| **Precondition** | Greedy pricing enabled; foreign currency pricelist |
| **Steps** | 1. Create order for 9 days with foreign currency |
| **Expected** | Each tier's price converted separately; total in pricelist currency |
| **Result** | |
