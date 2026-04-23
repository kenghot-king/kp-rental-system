# Test Cases: Damage Assessment & Fees

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Rental product (serialized preferred)
- Damage location configured
- Inspection location configured
- Items picked up and in "return" status

---

## 1. Damage Fee Creation

### TC-DM-001: Return with "damaged" condition adds fee line

| Field | Value |
|-------|-------|
| **Precondition** | Item picked up; return wizard open |
| **Steps** | 1. Set condition = "damaged"<br>2. Enter `damage_fee = 2,000`<br>3. Enter `damage_reason = "Screen cracked"`<br>4. Validate |
| **Expected** | New order line created with damage fee = 2,000; `damage_reason` stored |
| **Result** | |

### TC-DM-002: Return with "good" condition adds no fee

| Field | Value |
|-------|-------|
| **Precondition** | Item picked up |
| **Steps** | 1. Set condition = "good"; damage_fee = 0<br>2. Validate |
| **Expected** | No damage fee line added |
| **Result** | |

### TC-DM-003: Return with "inspect" condition adds no immediate fee

| Field | Value |
|-------|-------|
| **Precondition** | Item picked up |
| **Steps** | 1. Set condition = "inspect"<br>2. Validate |
| **Expected** | Item routed to inspection location; no fee line (pending inspection) |
| **Result** | |

### TC-DM-004: Damage fee line uses damage product

| Field | Value |
|-------|-------|
| **Precondition** | Damage triggered |
| **Steps** | 1. Check order line after damaged return |
| **Expected** | Line product is the configured damage fee product |
| **Result** | |

---

## 2. Damage Log Records

### TC-DM-005: Damage log created for each damaged item

| Field | Value |
|-------|-------|
| **Precondition** | 1 unit returned as damaged |
| **Steps** | 1. Return 1 unit as damaged with fee 1,000 |
| **Expected** | 1 `rental.damage.log` record created with: order_id, order_line_id, product_id, damage_fee=1,000, date=now |
| **Result** | |

### TC-DM-006: Damage log links to serial number if serialized

| Field | Value |
|-------|-------|
| **Precondition** | Serialized product; SN001 returned as damaged |
| **Steps** | 1. Return SN001 as damaged |
| **Expected** | Damage log `lot_id = SN001` |
| **Result** | |

### TC-DM-007: Damage log has no lot for non-serialized items

| Field | Value |
|-------|-------|
| **Precondition** | Non-serialized product returned as damaged |
| **Steps** | 1. Return 1 unit as damaged |
| **Expected** | `rental.damage.log` created with `lot_id = None` |
| **Result** | |

### TC-DM-008: Damage log stores reason text

| Field | Value |
|-------|-------|
| **Precondition** | Damage wizard with reason entered |
| **Steps** | 1. Return as damaged; reason = "Broken lens"<br>2. Check damage log |
| **Expected** | `reason = "Broken lens"` stored in log |
| **Result** | |

### TC-DM-009: Damage log records assessor (user_id)

| Field | Value |
|-------|-------|
| **Precondition** | User "John" processing return |
| **Steps** | 1. Return as damaged |
| **Expected** | `user_id = John` in damage log |
| **Result** | |

### TC-DM-010: Damage log date defaults to current datetime

| Field | Value |
|-------|-------|
| **Precondition** | New damage during return |
| **Steps** | 1. Return as damaged<br>2. Check damage log date |
| **Expected** | `date` ≈ now (current datetime at time of return) |
| **Result** | |

---

## 3. Serial Number Fee Splitting

### TC-DM-011: Multiple damaged serials — fee split equally

| Field | Value |
|-------|-------|
| **Precondition** | 2 serials returned as damaged; total fee = 2,000 |
| **Steps** | 1. Return SN001, SN002 as damaged with fee = 2,000<br>2. Validate |
| **Expected** | Fee split: SN001 = 1,000, SN002 = 1,000; or 1 line per serial each = 1,000 |
| **Result** | |

### TC-DM-012: 3 damaged serials with uneven split rounds correctly

| Field | Value |
|-------|-------|
| **Precondition** | 3 serials damaged; fee = 1,000 |
| **Steps** | 1. Return 3 serials as damaged; fee = 1,000 |
| **Expected** | Fee allocated per serial; total = 1,000 (rounding handled) |
| **Result** | |

---

## 4. Stock Routing by Condition

### TC-DM-013: Damaged items go to damage location

| Field | Value |
|-------|-------|
| **Precondition** | Company `damage_loc_id` configured |
| **Steps** | 1. Return 1 unit as damaged |
| **Expected** | Return stock move destination = `damage_loc_id` |
| **Result** | |

### TC-DM-014: Inspect items go to inspection location

| Field | Value |
|-------|-------|
| **Precondition** | Company `inspection_loc_id` configured |
| **Steps** | 1. Return 1 unit as "inspect" |
| **Expected** | Return stock move destination = `inspection_loc_id` |
| **Result** | |

### TC-DM-015: Good items return to main stock

| Field | Value |
|-------|-------|
| **Precondition** | Standard warehouse stock location |
| **Steps** | 1. Return 1 unit as "good" |
| **Expected** | Return move destination = `warehouse.lot_stock_id` |
| **Result** | |
