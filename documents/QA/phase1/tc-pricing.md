# Test Cases: Rental Pricing

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- Rental products configured with `rent_ok=True`
- Rental period recurrences exist (hourly, daily, weekly at minimum)
- Company rental settings configured

---

## 1. Single-Period Pricing

### TC-PR-001: Daily pricing for exact days

| Field | Value |
|-------|-------|
| **Precondition** | Product with pricing: 100 THB/day |
| **Steps** | 1. Create rental order with duration = 3 days exactly<br>2. Add product to order |
| **Expected** | Line price = 300 THB |
| **Result** | |

### TC-PR-002: Daily pricing rounds up partial day

| Field | Value |
|-------|-------|
| **Precondition** | Product with pricing: 100 THB/day |
| **Steps** | 1. Create rental order with duration = 2 days 3 hours<br>2. Add product to order |
| **Expected** | Line price = 300 THB (rounds up to 3 days) |
| **Result** | |

### TC-PR-003: Hourly pricing

| Field | Value |
|-------|-------|
| **Precondition** | Product with pricing: 20 THB/hour |
| **Steps** | 1. Create rental order with duration = 5 hours<br>2. Add product to order |
| **Expected** | Line price = 100 THB |
| **Result** | |

---

## 2. Best Pricing Rule Selection

### TC-PR-004: Weekly rate cheaper than daily for 7 days

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily=100 THB and weekly=500 THB |
| **Steps** | 1. Create rental order with duration = 7 days<br>2. Add product |
| **Expected** | System selects weekly rate, line price = 500 THB |
| **Result** | |

### TC-PR-005: Daily rate cheaper than weekly for 3 days

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily=100 THB and weekly=500 THB |
| **Steps** | 1. Create rental order with duration = 3 days<br>2. Add product |
| **Expected** | System selects daily rate, line price = 300 THB |
| **Result** | |

### TC-PR-006: Mixed period calculation

| Field | Value |
|-------|-------|
| **Precondition** | Product with daily=100 THB and weekly=500 THB |
| **Steps** | 1. Create rental order with duration = 10 days<br>2. Add product |
| **Expected** | System selects cheapest combination (1 week + 3 days = 800 THB) |
| **Result** | |

---

## 3. Pricelist-Specific Pricing

### TC-PR-007: VIP pricelist pricing

| Field | Value |
|-------|-------|
| **Precondition** | Product with default daily=100 THB. VIP pricelist with daily=80 THB. Customer assigned VIP pricelist |
| **Steps** | 1. Create rental order for VIP customer, duration = 3 days<br>2. Add product |
| **Expected** | Line price = 240 THB (VIP rate) |
| **Result** | |

### TC-PR-008: No pricelist-specific pricing falls back

| Field | Value |
|-------|-------|
| **Precondition** | Product with default daily=100 THB. Customer has pricelist with no rental pricing for this product |
| **Steps** | 1. Create rental order, duration = 3 days<br>2. Add product |
| **Expected** | Line price = 300 THB (default pricing) |
| **Result** | |

---

## 4. Variant-Specific Pricing

### TC-PR-009: Variant with specific pricing

| Field | Value |
|-------|-------|
| **Precondition** | Product with variants: "Large" daily=150 THB, "Small" daily=100 THB |
| **Steps** | 1. Create rental order, duration = 3 days<br>2. Add "Large" variant |
| **Expected** | Line price = 450 THB (150 × 3) |
| **Result** | |

### TC-PR-010: Variant without specific pricing uses template pricing

| Field | Value |
|-------|-------|
| **Precondition** | Product template with daily=100 THB. Variant has no specific pricing |
| **Steps** | 1. Create rental order, duration = 3 days<br>2. Add variant |
| **Expected** | Line price = 300 THB (template pricing) |
| **Result** | |

---

## 5. Overnight Period Pricing

### TC-PR-011: Overnight pricing applied

| Field | Value |
|-------|-------|
| **Precondition** | Product with overnight recurrence (24hr, pickup_time=14:00, return_time=12:00) at 200 THB/night |
| **Steps** | 1. Create rental order for 2 nights<br>2. Add product |
| **Expected** | Line price = 400 THB |
| **Result** | |

---

## 6. Display Price & Configuration

### TC-PR-012: Display price on product

| Field | Value |
|-------|-------|
| **Precondition** | Product with pricing 100 THB/day |
| **Steps** | 1. Go to Rental > Products<br>2. Find product in list |
| **Expected** | Product shows display_price = "100.00 THB / 1 Day" |
| **Result** | |

### TC-PR-013: Create new recurrence

| Field | Value |
|-------|-------|
| **Precondition** | Manager role |
| **Steps** | 1. Go to Rental > Configuration > Rental Periods<br>2. Create new: duration=3, unit=day, name="3-Day" |
| **Expected** | Recurrence created, available in product pricing dropdown, duration_display = "3 Days" |
| **Result** | |

### TC-PR-014: Deactivate recurrence

| Field | Value |
|-------|-------|
| **Precondition** | Existing recurrence not used by any active pricing |
| **Steps** | 1. Open recurrence record<br>2. Set active=False (archive) |
| **Expected** | Recurrence no longer appears in product pricing dropdown |
| **Result** | |
