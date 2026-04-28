# Test Cases: Rental Order Management

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- At least 1 rental product configured with `rent_ok=True` and daily pricing
- Company rental settings configured (rental location exists)
- User logged in with Salesman or Manager role

---

## 1. Order Creation & Date Validation

### TC-RO-001: Create rental order with dates

| Field | Value |
|-------|-------|
| **Precondition** | Rental product exists with daily pricing |
| **Steps** | 1. Go to Rental > Orders > New<br>2. Set start_date = 2026-04-10 09:00<br>3. Set return_date = 2026-04-12 09:00<br>4. Add rental product line |
| **Expected** | Order created with duration_days=2, remaining_hours=0, rental_status="draft" |
| **Result** | |

### TC-RO-002: Auto-set dates if not provided

| Field | Value |
|-------|-------|
| **Precondition** | Rental product exists |
| **Steps** | 1. Go to Rental > Orders > New<br>2. Add a rental product line without setting dates |
| **Expected** | System auto-sets start_date ≈ now+1hr, return_date ≈ now+25hrs |
| **Result** | |

### TC-RO-003: Invalid dates rejected

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft |
| **Steps** | 1. Set return_date earlier than or equal to start_date<br>2. Try to save |
| **Expected** | System raises a validation error preventing save |
| **Result** | |

### TC-RO-004: Duration computed — calendar-day model

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft |
| **Steps** | 1. Set start_date = 2026-04-10 09:00<br>2. Set return_date = 2026-04-12 14:00 |
| **Expected** | Duration shows **2 days** (no hours — partial day absorbed by calendar-day model) |
| **Result** | |

---

## 2. Status Transitions

### TC-RO-005: Draft to sent

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft with product lines |
| **Steps** | 1. Click "Send by Email" or "Send Quotation" |
| **Expected** | rental_status changes to "sent", status badge updates |
| **Result** | |

### TC-RO-006: Sent to pickup on confirm

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in "sent" status |
| **Steps** | 1. Click "Confirm" |
| **Expected** | rental_status = "pickup", delivery stock move is created |
| **Result** | |

### TC-RO-007: Pickup to return after full pickup

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with all items reserved |
| **Steps** | 1. Click "Pickup" button<br>2. Confirm all quantities in wizard<br>3. Click "Validate" |
| **Expected** | rental_status = "return" |
| **Result** | |

### TC-RO-008: Return to returned after full return

| Field | Value |
|-------|-------|
| **Precondition** | Order with all items picked up (status = "return") |
| **Steps** | 1. Click "Return" button<br>2. Confirm all quantities in wizard<br>3. Click "Validate" |
| **Expected** | rental_status = "returned" |
| **Result** | |

### TC-RO-009: Partial pickup stays in pickup

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with 5 units reserved |
| **Steps** | 1. Click "Pickup"<br>2. Set qty_delivered = 3 in wizard<br>3. Validate |
| **Expected** | rental_status remains "pickup", Pickup button still visible |
| **Result** | |

### TC-RO-010: Partial return stays in return

| Field | Value |
|-------|-------|
| **Precondition** | Order with 5 units picked up |
| **Steps** | 1. Click "Return"<br>2. Set qty_returned = 2 in wizard<br>3. Validate |
| **Expected** | rental_status remains "return", Return button still visible |
| **Result** | |

---

## 3. Cancel Order

### TC-RO-011: Cancel with picked-up items

| Field | Value |
|-------|-------|
| **Precondition** | Order with items picked up (qty_delivered > qty_returned) |
| **Steps** | 1. Click "Cancel" on the order |
| **Expected** | System auto-returns outstanding items, creates return stock moves, state = "cancel" |
| **Result** | |

### TC-RO-012: Cancel draft order

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft status |
| **Steps** | 1. Click "Cancel" |
| **Expected** | Order cancelled, no stock moves created |
| **Result** | |

---

## 4. Late Detection

### TC-RO-013: Late pickup detected

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with start_date in the past, items not yet picked up |
| **Steps** | 1. Open the order form |
| **Expected** | is_late=True, status badge shows "Late Pickup" (red) |
| **Result** | |

### TC-RO-014: Late return detected

| Field | Value |
|-------|-------|
| **Precondition** | Order with items picked up, return_date in the past |
| **Steps** | 1. Open the order form |
| **Expected** | is_late=True, status badge shows "Late Return" (red) |
| **Result** | |

### TC-RO-015: On-time order not marked late

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with start_date in the future |
| **Steps** | 1. Open the order form |
| **Expected** | is_late=False, badge shows "Booked" (normal color) |
| **Result** | |

---

## 5. Price Update on Date Change

### TC-RO-016: Extend rental period

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with product priced at 100 THB/day, current duration = 3 days (price = 300) |
| **Steps** | 1. Change return_date to extend to 5 days<br>2. Click "Update Rental Prices" |
| **Expected** | Line price recalculates to 500 THB |
| **Result** | |

### TC-RO-017: Shorten rental period

| Field | Value |
|-------|-------|
| **Precondition** | Order with 7-day duration, price = 700 THB |
| **Steps** | 1. Change return_date to 3 days<br>2. Click "Update Rental Prices" |
| **Expected** | Line price recalculates to 300 THB |
| **Result** | |
