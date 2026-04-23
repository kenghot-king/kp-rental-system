# Test Cases: Late & Delay Fees

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Rental product with `extra_hourly` and/or `extra_daily` configured
- Company setting: `min_extra_hour` configured (grace period)
- Order confirmed with items picked up; return date has passed

---

## 1. Late Detection

### TC-LF-001: is_late = True when return date passed + grace exceeded

| Field | Value |
|-------|-------|
| **Precondition** | Order in "return" status; `return_date` + `min_extra_hour` < now |
| **Steps** | 1. Check `is_late` on order |
| **Expected** | `is_late = True` |
| **Result** | |

### TC-LF-002: is_late = False within grace period

| Field | Value |
|-------|-------|
| **Precondition** | `return_date` has passed but within `min_extra_hour` grace |
| **Steps** | 1. Check `is_late` |
| **Expected** | `is_late = False` |
| **Result** | |

### TC-LF-003: is_late = False when order in "pickup" status

| Field | Value |
|-------|-------|
| **Precondition** | Order in "pickup" status; `rental_start_date` passed |
| **Steps** | 1. Check `is_late` |
| **Expected** | `is_late = False` (late only applies to return status) |
| **Result** | |

### TC-LF-004: is_late = False when all items returned

| Field | Value |
|-------|-------|
| **Precondition** | All items returned; status = "returned" |
| **Steps** | 1. Check `is_late` |
| **Expected** | `is_late = False` |
| **Result** | |

### TC-LF-005: Late badge/indicator shown in order list view

| Field | Value |
|-------|-------|
| **Precondition** | Multiple orders; some late, some not |
| **Steps** | 1. Go to Rental > Orders list view |
| **Expected** | Late orders highlighted or tagged distinctly |
| **Result** | |

---

## 2. Delay Fee Calculation

### TC-LF-006: Delay fee generated on late return

| Field | Value |
|-------|-------|
| **Precondition** | Product has `extra_daily = 300`; return 2 days late |
| **Steps** | 1. Return items 2 days after due date<br>2. Check order lines |
| **Expected** | Delay fee line added: 2 days × 300 = 600 |
| **Result** | |

### TC-LF-007: Delay fee uses hourly rate for short overdue

| Field | Value |
|-------|-------|
| **Precondition** | Product has `extra_hourly = 50`; returned 3 hours late |
| **Steps** | 1. Return items 3 hours after due date |
| **Expected** | Delay fee line: 3 × 50 = 150 |
| **Result** | |

### TC-LF-008: Delay fee not charged within grace period

| Field | Value |
|-------|-------|
| **Precondition** | `min_extra_hour = 2`; returned 1 hour late |
| **Steps** | 1. Return items 1 hour after due date |
| **Expected** | No delay fee line added |
| **Result** | |

### TC-LF-009: Delay fee line linked to RENTAL product

| Field | Value |
|-------|-------|
| **Precondition** | Delay fee triggered |
| **Steps** | 1. Check the delay fee order line |
| **Expected** | Line uses "RENTAL" product (or configured late fee product) |
| **Result** | |

### TC-LF-010: Delay fee with currency conversion

| Field | Value |
|-------|-------|
| **Precondition** | Product price in THB; order uses USD pricelist |
| **Steps** | 1. Return late; check delay fee |
| **Expected** | Delay fee converted to order currency using current rate |
| **Result** | |

---

## 3. Return Wizard Late Indicator

### TC-LF-011: Wizard shows is_late flag when overdue

| Field | Value |
|-------|-------|
| **Precondition** | Items overdue; return date + grace exceeded |
| **Steps** | 1. Open return wizard |
| **Expected** | Wizard shows "Late return" warning or `is_late = True` indicator |
| **Result** | |

### TC-LF-012: Wizard shows is_late = False when on-time

| Field | Value |
|-------|-------|
| **Precondition** | Returning within rental period |
| **Steps** | 1. Open return wizard before due date |
| **Expected** | No late warning shown |
| **Result** | |

---

## 4. Edge Cases

### TC-LF-013: Zero extra rates — no delay fee line created

| Field | Value |
|-------|-------|
| **Precondition** | `extra_hourly = 0`, `extra_daily = 0`; return late |
| **Steps** | 1. Return items late |
| **Expected** | No delay fee line added (zero fee suppressed) |
| **Result** | |

### TC-LF-014: Delay fee added as new sale order line

| Field | Value |
|-------|-------|
| **Precondition** | Delay fee triggered |
| **Steps** | 1. Check order lines after late return |
| **Expected** | New `sale.order.line` created via Command.create(); existing lines unchanged |
| **Result** | |

### TC-LF-015: Delay fee fallback — RENTAL product created if not found

| Field | Value |
|-------|-------|
| **Precondition** | No "RENTAL" product exists in database |
| **Steps** | 1. Trigger late return |
| **Expected** | System creates a RENTAL service product and uses it for fee line |
| **Result** | |
