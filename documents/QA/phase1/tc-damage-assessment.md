# Test Cases: Damage Assessment

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- 2 rental products: 1 non-tracked (bulk), 1 serial-tracked with serials in stock
- Company rental settings configured (damage_product optional — test both with and without)
- Confirmed rental order with items picked up, ready for return

---

## 1. Condition Assessment UI

### TC-DA-001: Return item in good condition

| Field | Value |
|-------|-------|
| **Precondition** | Order with items picked up |
| **Steps** | 1. Click "Return"<br>2. Set condition = "Good" (default)<br>3. Validate |
| **Expected** | No damage fee line created, no damage log record, item returned normally |
| **Result** | |

### TC-DA-002: Return item as damaged with fee

| Field | Value |
|-------|-------|
| **Precondition** | Order with items picked up |
| **Steps** | 1. Click "Return"<br>2. Set condition = "Damaged"<br>3. Enter damage_fee = 500<br>4. Enter damage_reason = "Scratched surface"<br>5. Validate |
| **Expected** | Damage fee SO line created with price=500, description includes "Scratched surface" |
| **Result** | |

### TC-DA-003: Damage fields hidden when condition is good

| Field | Value |
|-------|-------|
| **Precondition** | Return wizard open |
| **Steps** | 1. Verify condition = "Good" (default) |
| **Expected** | damage_fee and damage_reason fields are not visible |
| **Result** | |

### TC-DA-004: Damage fields shown when condition is damaged

| Field | Value |
|-------|-------|
| **Precondition** | Return wizard open |
| **Steps** | 1. Change condition to "Damaged" |
| **Expected** | damage_fee and damage_reason fields become visible |
| **Result** | |

### TC-DA-005: Damage fields hidden during pickup

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order, items not yet picked up |
| **Steps** | 1. Click "Pickup" to open wizard |
| **Expected** | condition, damage_fee, damage_reason columns are not visible in wizard |
| **Result** | |

---

## 2. Damage Fee SO Line Creation

### TC-DA-006: Damage line uses configured damage product

| Field | Value |
|-------|-------|
| **Precondition** | company.damage_product set to "Damage Fee" service product |
| **Steps** | 1. Return item as damaged with fee=500 |
| **Expected** | Damage SO line uses the configured "Damage Fee" product |
| **Result** | |

### TC-DA-007: Damage product auto-created if not configured

| Field | Value |
|-------|-------|
| **Precondition** | company.damage_product is not set (empty) |
| **Steps** | 1. Return item as damaged with fee=500 |
| **Expected** | System auto-creates "Rental Damage Fee" service product (default_code="DAMAGE") and uses it |
| **Result** | |

### TC-DA-008: Damage line not marked as rental

| Field | Value |
|-------|-------|
| **Precondition** | Damage fee line created from return |
| **Steps** | 1. Check the damage SO line on the order |
| **Expected** | is_rental=False (will be invoiced as regular service, not rental) |
| **Result** | |

---

## 3. Damage Log Records

### TC-DA-009: Damage log created for bulk product

| Field | Value |
|-------|-------|
| **Precondition** | Bulk (non-tracked) product returned as damaged, fee=500 |
| **Steps** | 1. Return as damaged with fee=500, reason="Broken handle"<br>2. Check rental.damage.log records |
| **Expected** | 1 damage log created: lot_id=False, damage_fee=500, reason="Broken handle", order_id, product_id, user_id=current user |
| **Result** | |

### TC-DA-010: Damage log created per serial

| Field | Value |
|-------|-------|
| **Precondition** | Serial-tracked product with 3 serials (SN001, SN002, SN003) picked up |
| **Steps** | 1. Return all 3 as damaged, total fee=900<br>2. Check rental.damage.log records |
| **Expected** | 3 damage logs created, each with fee=300 (900/3), each linked to its respective serial |
| **Result** | |

### TC-DA-011: Damage fee split equally across serials

| Field | Value |
|-------|-------|
| **Precondition** | 2 serials picked up |
| **Steps** | 1. Return both as damaged, total damage_fee=500<br>2. Check SO lines and damage logs |
| **Expected** | 2 damage SO lines (each 250 THB), 2 damage logs (each fee=250) |
| **Result** | |

---

## 4. Damage History & Configuration

### TC-DA-012: Damage count on serial form

| Field | Value |
|-------|-------|
| **Precondition** | Serial SN001 has been damaged in 2 separate rental orders |
| **Steps** | 1. Go to Inventory > Lots/Serial Numbers<br>2. Open SN001 |
| **Expected** | damage_count=2, smart button shows "Damage History (2)" |
| **Result** | |

### TC-DA-013: View damage logs from serial

| Field | Value |
|-------|-------|
| **Precondition** | Serial with damage history |
| **Steps** | 1. Open serial form<br>2. Click "Damage History" smart button |
| **Expected** | List view shows all rental.damage.log records for this serial: dates, orders, fees, reasons |
| **Result** | |

### TC-DA-014: Set damage product in settings

| Field | Value |
|-------|-------|
| **Precondition** | Admin access |
| **Steps** | 1. Go to Rental > Configuration > Settings<br>2. Set damage_product to a service product<br>3. Save |
| **Expected** | Subsequent damage assessments use the configured product for the damage SO line |
| **Result** | |
