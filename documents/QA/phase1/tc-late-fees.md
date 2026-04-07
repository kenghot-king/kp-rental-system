# Test Cases: Late Fee Calculation

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- Rental product with `rent_ok=True`
- Company settings: extra_hour (hourly late fee), extra_day (daily late fee), min_extra_hour (grace period, default=2)
- Confirmed rental order with items picked up
- Return date is in the past (to trigger late return scenarios)

---

## 1. Late Fee Calculation Scenarios

### TC-LF-001: Return on time — no late fee

| Field | Value |
|-------|-------|
| **Precondition** | Order with return_date = 2026-04-12 09:00 |
| **Steps** | 1. Return items at 2026-04-12 08:30 (before return_date) |
| **Expected** | No delay line created on the SO |
| **Result** | |

### TC-LF-002: Return within grace period — no late fee

| Field | Value |
|-------|-------|
| **Precondition** | min_extra_hour=2, return_date = 2026-04-12 09:00 |
| **Steps** | 1. Return items at 2026-04-12 10:30 (1.5 hrs late, within 2-hr grace) |
| **Expected** | No delay line created |
| **Result** | |

### TC-LF-003: Return after grace period — late fee created

| Field | Value |
|-------|-------|
| **Precondition** | min_extra_hour=2, return_date = 2026-04-12 09:00, extra_hourly=50, extra_daily=0 |
| **Steps** | 1. Return items at 2026-04-12 14:00 (5 hrs late) |
| **Expected** | Delay line created with price = 5 × 50 = 250 THB |
| **Result** | |

### TC-LF-004: Late by days and hours

| Field | Value |
|-------|-------|
| **Precondition** | return_date = 2026-04-12 09:00, extra_hourly=50, extra_daily=200 |
| **Steps** | 1. Return items at 2026-04-14 14:00 (2 days 5 hrs late) |
| **Expected** | Delay line created with price = (2 × 200) + (5 × 50) = 650 THB |
| **Result** | |

### TC-LF-005: Late fee uses company delay product

| Field | Value |
|-------|-------|
| **Precondition** | company.extra_product set to "Late Return Fee" service product |
| **Steps** | 1. Trigger a late return |
| **Expected** | Delay SO line uses the configured "Late Return Fee" product |
| **Result** | |

### TC-LF-006: Delay product auto-created if not configured

| Field | Value |
|-------|-------|
| **Precondition** | company.extra_product is not set (empty) |
| **Steps** | 1. Trigger a late return |
| **Expected** | System auto-creates "Rental Delay Cost" service product (default_code="DELAY") and uses it |
| **Result** | |

---

## 2. Product-Level Override & Grace Period

### TC-LF-007: Product-specific late fees

| Field | Value |
|-------|-------|
| **Precondition** | Product extra_hourly=100 (company default=50) |
| **Steps** | 1. Trigger late return, 3 hours late |
| **Expected** | Delay line uses product rate: 3 × 100 = 300 THB |
| **Result** | |

### TC-LF-008: Product without override uses company default

| Field | Value |
|-------|-------|
| **Precondition** | Product extra_hourly=0 (not set), company extra_hour=50 |
| **Steps** | 1. Trigger late return, 3 hours late |
| **Expected** | Delay line uses company rate: 3 × 50 = 150 THB |
| **Result** | |

### TC-LF-009: Change grace period

| Field | Value |
|-------|-------|
| **Precondition** | Admin access, current min_extra_hour=2 |
| **Steps** | 1. Go to Rental > Configuration > Settings<br>2. Change min_extra_hour to 4<br>3. Save<br>4. Return an item 3 hours late |
| **Expected** | No late fee charged (3 hours < 4 hour grace period) |
| **Result** | |
