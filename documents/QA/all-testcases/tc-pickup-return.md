# Test Cases: Pickup & Return Process

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Confirmed rental order with products in stock
- Rental locations configured: source location (stock), rental location, return locations
- User has Salesman or Manager role

---

## 1. Pickup Wizard

### TC-PK-001: Open pickup wizard

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in "pickup" status |
| **Steps** | 1. Click "Pickup" button on order |
| **Expected** | Rental processing wizard opens with status=pickup; all rental lines listed |
| **Result** | |

### TC-PK-002: Wizard shows correct available quantity

| Field | Value |
|-------|-------|
| **Precondition** | 5 units in stock; 2 reserved for this order |
| **Steps** | 1. Open pickup wizard |
| **Expected** | `qty_reserved = 2`; qty field pre-filled with 2 |
| **Result** | |

### TC-PK-003: Full pickup — validate all quantities

| Field | Value |
|-------|-------|
| **Precondition** | Order for 2 units; 2 in stock |
| **Steps** | 1. Open pickup wizard<br>2. Leave qty = 2 (default)<br>3. Click "Validate" |
| **Expected** | `qty_delivered = 2`; delivery move validated; `rental_status = return` |
| **Result** | |

### TC-PK-004: Partial pickup — enter qty less than ordered

| Field | Value |
|-------|-------|
| **Precondition** | Order for 3 units |
| **Steps** | 1. Open pickup wizard<br>2. Set qty = 2<br>3. Validate |
| **Expected** | `qty_delivered = 2`; order stays in "pickup" status (1 still pickable) |
| **Result** | |

### TC-PK-005: Pickup quantity cannot exceed ordered quantity

| Field | Value |
|-------|-------|
| **Precondition** | Order for 2 units |
| **Steps** | 1. Open pickup wizard<br>2. Enter qty = 3<br>3. Try to validate |
| **Expected** | Validation error: cannot deliver more than ordered |
| **Result** | |

### TC-PK-006: Pickup creates delivery stock move

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order |
| **Steps** | 1. Complete pickup for 2 units |
| **Expected** | Stock move from stock location to rental location created and validated |
| **Result** | |

### TC-PK-007: Chatter updated after pickup

| Field | Value |
|-------|-------|
| **Precondition** | Order in pickup status |
| **Steps** | 1. Complete pickup via wizard |
| **Expected** | Chatter shows "Pickup: <product> → 2 units" message |
| **Result** | |

### TC-PK-008: Multiple sequential pickups for same order

| Field | Value |
|-------|-------|
| **Precondition** | Order for 3 units; first pickup = 1 |
| **Steps** | 1. Pickup 1 unit<br>2. Open pickup wizard again<br>3. Pickup remaining 2 |
| **Expected** | Total `qty_delivered = 3`; status changes to "return" after second pickup |
| **Result** | |

---

## 2. Return Wizard

### TC-PK-009: Open return wizard

| Field | Value |
|-------|-------|
| **Precondition** | All items picked up; order in "return" status |
| **Steps** | 1. Click "Return" button |
| **Expected** | Return wizard opens with status=return; all picked-up lines listed |
| **Result** | |

### TC-PK-010: Full return — good condition

| Field | Value |
|-------|-------|
| **Precondition** | 2 units out; wizard open |
| **Steps** | 1. Set qty = 2, condition = "good"<br>2. Validate |
| **Expected** | `qty_returned = 2`; stock moved to main stock; `rental_status = returned` |
| **Result** | |

### TC-PK-011: Return — damaged condition routes to damage location

| Field | Value |
|-------|-------|
| **Precondition** | Company damage location configured |
| **Steps** | 1. Set condition = "damaged"<br>2. Enter damage fee = 1,000<br>3. Validate |
| **Expected** | Stock moved to damage location; damage fee line added to order; damage log created |
| **Result** | |

### TC-PK-012: Return — inspect condition routes to inspection location

| Field | Value |
|-------|-------|
| **Precondition** | Inspection location configured |
| **Steps** | 1. Set condition = "inspect"<br>2. Validate |
| **Expected** | Stock moved to inspection location |
| **Result** | |

### TC-PK-013: Return quantity cannot exceed picked-up quantity

| Field | Value |
|-------|-------|
| **Precondition** | 2 units delivered |
| **Steps** | 1. Open return wizard<br>2. Enter qty = 3<br>3. Try to validate |
| **Expected** | Validation error: cannot return more than delivered |
| **Result** | |

### TC-PK-014: Partial return — order stays in "return" status

| Field | Value |
|-------|-------|
| **Precondition** | 3 units delivered |
| **Steps** | 1. Return 2 units |
| **Expected** | `qty_returned = 2`; order stays in "return" status (1 still out) |
| **Result** | |

### TC-PK-015: Second partial return — completes the order

| Field | Value |
|-------|-------|
| **Precondition** | 1 unit still out after first partial return |
| **Steps** | 1. Return remaining 1 unit |
| **Expected** | `rental_status = returned`; all lines show returned ≥ delivered |
| **Result** | |

### TC-PK-016: Chatter updated after return

| Field | Value |
|-------|-------|
| **Precondition** | Order in return status |
| **Steps** | 1. Complete return via wizard |
| **Expected** | Chatter shows "Return: <product> → 2 units" message |
| **Result** | |

### TC-PK-017: Late return shows is_late warning in wizard

| Field | Value |
|-------|-------|
| **Precondition** | Return date has passed; `min_extra_hour` buffer exceeded |
| **Steps** | 1. Open return wizard after due date |
| **Expected** | `is_late = True`; wizard shows late indicator |
| **Result** | |

---

## 3. Return with Multiple Conditions (Mixed)

### TC-PK-018: Return some units as good, some as damaged

| Field | Value |
|-------|-------|
| **Precondition** | 2 non-serialized units out |
| **Steps** | 1. Return 1 unit as "good"<br>2. Return 1 unit as "damaged" with fee<br>3. Validate |
| **Expected** | 1 unit → stock location; 1 unit → damage location; 1 damage fee line added |
| **Result** | |

---

## 4. Line-Level Rental Status

### TC-PK-019: Line rental_status = pickup before any delivery

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order, no deliveries yet |
| **Steps** | 1. Check `rental_status` on individual line |
| **Expected** | `pickup` |
| **Result** | |

### TC-PK-020: Line rental_status = return after full delivery

| Field | Value |
|-------|-------|
| **Precondition** | All qty delivered; not yet returned |
| **Steps** | 1. Check line `rental_status` |
| **Expected** | `return` |
| **Result** | |

### TC-PK-021: Line rental_status = returned after full return

| Field | Value |
|-------|-------|
| **Precondition** | All qty returned |
| **Steps** | 1. Check line `rental_status` |
| **Expected** | `returned` |
| **Result** | |

---

## 5. Rental Notes on Line

### TC-PK-022: Pickup notes appended to line name

| Field | Value |
|-------|-------|
| **Precondition** | Rental line for Camera × 2 |
| **Steps** | 1. Complete pickup for 2 units |
| **Expected** | Line name contains section after `\n---` with "Picked up: 2" |
| **Result** | |

### TC-PK-023: Return notes appended to line name

| Field | Value |
|-------|-------|
| **Precondition** | 2 units picked up |
| **Steps** | 1. Return 2 units |
| **Expected** | Line name updated with "Returned: 2" note after separator |
| **Result** | |

---

## 6. Product Updatability on Rental Lines

### TC-PK-024: Rental line product can be changed even after confirm

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with rental line |
| **Steps** | 1. Open order line<br>2. Try to change the product |
| **Expected** | Product field is editable (`product_updatable=True`) |
| **Result** | |

---

## 7. Line Display Name with Dates

### TC-PK-025: Rental line display name shows period

| Field | Value |
|-------|-------|
| **Precondition** | Rental line with start = 2026-05-01, return = 2026-05-03 |
| **Steps** | 1. Check line display name in order |
| **Expected** | Shows "\n01/05/26 to 03/05/26" or similar date range |
| **Result** | |

### TC-PK-026: Single-day rental shows time only for return

| Field | Value |
|-------|-------|
| **Precondition** | start = 2026-05-01 09:00, return = 2026-05-01 17:00 (same day) |
| **Steps** | 1. Check line display name |
| **Expected** | Shows "01/05/26 09:00 to 17:00" (return date shows time only) |
| **Result** | |

---

## 8. Gantt Schedule Write

### TC-PK-027: Gantt drag changes start date when status = pickup

| Field | Value |
|-------|-------|
| **Precondition** | Order in "pickup" status (not yet returned) |
| **Steps** | 1. Drag rental line in Gantt to shift start date forward |
| **Expected** | Start date updated; price recalculated |
| **Result** | |

### TC-PK-028: Gantt drag blocked for start date when status = return or returned

| Field | Value |
|-------|-------|
| **Precondition** | Items already picked up; status = "return" |
| **Steps** | 1. Try to drag start date in Gantt |
| **Expected** | Error: cannot change start date after pickup |
| **Result** | |

### TC-PK-029: Gantt drag blocked for return date when status = returned

| Field | Value |
|-------|-------|
| **Precondition** | All items returned; status = "returned" |
| **Steps** | 1. Try to drag return date in Gantt |
| **Expected** | Error: cannot change return date after return |
| **Result** | |

### TC-PK-030: Gantt drag shows success notification

| Field | Value |
|-------|-------|
| **Precondition** | Order in draft/sent status |
| **Steps** | 1. Drag line in Gantt to new dates |
| **Expected** | Success notification displayed; dates updated |
| **Result** | |
