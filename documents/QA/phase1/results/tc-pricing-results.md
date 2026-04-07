# Test Execution Results: Rental Pricing

**Module:** `ggg_rental`
**Environment:** Local Odoo (test_ce) via XML-RPC
**Test Script Executed:** `test_rental_tc.py`

## Summary
✅ **Total Executed:** 14/14
✅ **Passed:** 14
❌ **Failed:** 0
⚠️ **Blocked:** 0

---

## 1. Single-Period Pricing

### TC-PR-001: Daily pricing for exact days
- **Result:** `[PASS]`
- **Notes:** Verified via backend automation. Created a rental order for 3 days and added product. The `price_subtotal` was correctly computed as 300.0 THB.

### TC-PR-002: Daily pricing rounds up partial day
- **Result:** `[PASS]`
- **Notes:** Configured period 2 days 3 hours. System successfully rounded up to 3 pricing periods. Computed price 300 THB.

### TC-PR-003: Hourly pricing
- **Result:** `[PASS]`
- **Notes:** Verified creation of 5 hour rental for 20 THB/hour product. Computed line price is 100 THB.

---

## 2. Best Pricing Rule Selection

### TC-PR-004: Weekly rate cheaper than daily for 7 days
- **Result:** `[PASS]`
- **Notes:** Configured 7 days. Engine successfully evaluated 7x daily (700 THB) vs. weekly (500 THB) and selected the optimal weekly rate of 500 THB.

### TC-PR-005: Daily rate cheaper than weekly for 3 days
- **Result:** `[PASS]`
- **Notes:** 3 days correctly selected 3x daily (300 THB) over base weekly (500 THB).

### TC-PR-006: Mixed period calculation
- **Result:** `[PASS]`
- **Notes:** For a 10-day period, the rule evaluation properly combined 1 week (500 THB) + 3 days (300 THB) for a total of 800 THB.

---

## 3. Pricelist-Specific Pricing

### TC-PR-007: VIP pricelist pricing
- **Result:** `[PASS]`
- **Notes:** Verified pricelist resolution. Line price matched VIP rate of 240 THB for 3 days.

### TC-PR-008: No pricelist-specific pricing falls back
- **Result:** `[PASS]`
- **Notes:** Without a specific VIP rule, pricing safely fell back to the base `product.pricing` rule of 300 THB default.

---

## 4. Variant-Specific Pricing

### TC-PR-009: Variant with specific pricing
- **Result:** `[PASS]`
- **Notes:** Ordered the "Large" variant. 3 days correctly calculated at 150 THB/day = 450 THB.

### TC-PR-010: Variant without specific pricing uses template pricing
- **Result:** `[PASS]`
- **Notes:** Small variant safely used `product.template` fallback pricing. Line price was 300 THB.

---

## 5. Overnight Period Pricing

### TC-PR-011: Overnight pricing applied
- **Result:** `[PASS]`
- **Notes:** Created periods spanning overnight (14:00 to 12:00 the next day). Count calculated as 2 nights. Line price = 400 THB.

---

## 6. Display Price & Configuration

### TC-PR-012: Display price on product
- **Result:** `[PASS]`
- **Notes:** Display logic on `product.template` correctly binds to the defined recurrence format ("100.00 THB / 1 Day").

### TC-PR-013: Create new recurrence
- **Result:** `[PASS]`
- **Notes:** Created recurrence "3-Day" (unit=day, duration=3). Configuration is available in dropdown logic.

### TC-PR-014: Deactivate recurrence
- **Result:** `[PASS]`
- **Notes:** Archiving (active=False) properly filters recurrences from UI contexts and blocks new pricing creation.
