# Test Cases: Stock & Serial Number Tracking

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Rental product with `tracking = 'serial'`
- Serial numbers (lots) created and in stock
- Rental order confirmed

---

## 1. Serial Number Pickup

### TC-ST-001: Pickup wizard shows available serials

| Field | Value |
|-------|-------|
| **Precondition** | Serialized rental product; 3 serials in stock (SN001, SN002, SN003) |
| **Steps** | 1. Open pickup wizard |
| **Expected** | `pickeable_lot_ids` shows SN001, SN002, SN003 (serials in stock, not rented) |
| **Result** | |

### TC-ST-002: Pre-selected serials from delivery reservation

| Field | Value |
|-------|-------|
| **Precondition** | Delivery move reserved SN001 and SN002 |
| **Steps** | 1. Open pickup wizard |
| **Expected** | `pickedup_lot_ids` pre-populated with SN001, SN002 |
| **Result** | |

### TC-ST-003: Select serials for pickup

| Field | Value |
|-------|-------|
| **Precondition** | 3 available serials |
| **Steps** | 1. Select SN001 and SN003 in pickup wizard<br>2. Validate |
| **Expected** | `pickedup_lot_ids = [SN001, SN003]`; qty_delivered = 2; stock moved |
| **Result** | |

### TC-ST-004: Cannot pick up already-rented serial

| Field | Value |
|-------|-------|
| **Precondition** | SN001 is currently out on a different rental order |
| **Steps** | 1. Open pickup wizard for new order |
| **Expected** | SN001 not shown in `pickeable_lot_ids` |
| **Result** | |

### TC-ST-005: One stock move line per serial during pickup

| Field | Value |
|-------|-------|
| **Precondition** | Picking up 3 serials |
| **Steps** | 1. Complete pickup for SN001, SN002, SN003 |
| **Expected** | 3 stock move lines created (one per serial) |
| **Result** | |

---

## 2. Serial Number Return

### TC-ST-006: Return wizard shows only picked-up serials

| Field | Value |
|-------|-------|
| **Precondition** | SN001 and SN002 picked up; SN003 not picked up |
| **Steps** | 1. Open return wizard |
| **Expected** | `returnable_lot_ids = [SN001, SN002]`; SN003 not shown |
| **Result** | |

### TC-ST-007: Select specific serials to return

| Field | Value |
|-------|-------|
| **Precondition** | SN001 and SN002 out; returning only SN001 |
| **Steps** | 1. Select SN001 in return wizard<br>2. Validate |
| **Expected** | `returned_lot_ids = [SN001]`; SN002 still in `pickedup_lot_ids` |
| **Result** | |

### TC-ST-008: Full return of all serials

| Field | Value |
|-------|-------|
| **Precondition** | SN001 and SN002 out |
| **Steps** | 1. Select both serials in return wizard<br>2. Validate |
| **Expected** | `returned_lot_ids = [SN001, SN002]`; `rental_status = returned` |
| **Result** | |

### TC-ST-009: One return move line per serial

| Field | Value |
|-------|-------|
| **Precondition** | Returning 2 serials |
| **Steps** | 1. Complete return for SN001, SN002 |
| **Expected** | 2 stock move lines in return picking (1 per serial) |
| **Result** | |

### TC-ST-010: Cannot return serial that was not picked up

| Field | Value |
|-------|-------|
| **Precondition** | SN003 was never picked up |
| **Steps** | 1. Open return wizard |
| **Expected** | SN003 not in `returnable_lot_ids` |
| **Result** | |

---

## 3. Serial Number on Order Line

### TC-ST-011: Pickup notes show serial names

| Field | Value |
|-------|-------|
| **Precondition** | Picked up SN001, SN002 |
| **Steps** | 1. Check order line name after pickup |
| **Expected** | Name contains "Picked up: SN001, SN002" (or equivalent) |
| **Result** | |

### TC-ST-012: Return notes show returned serial names

| Field | Value |
|-------|-------|
| **Precondition** | SN001 returned |
| **Steps** | 1. Check order line name after partial return |
| **Expected** | Name contains "Returned: SN001" |
| **Result** | |

---

## 4. Serial Number Damage Split

### TC-ST-013: Damage fee split equally among damaged serials

| Field | Value |
|-------|-------|
| **Precondition** | 2 serials returned as damaged with total damage fee = 2,000 |
| **Steps** | 1. Return SN001, SN002 as "damaged"; fee = 2,000<br>2. Validate |
| **Expected** | 2 damage fee lines created: 1,000 each (or 1 line per serial split) |
| **Result** | |

### TC-ST-014: Damage log created per damaged serial

| Field | Value |
|-------|-------|
| **Precondition** | 2 serials returned as damaged |
| **Steps** | 1. Return SN001, SN002 as damaged |
| **Expected** | 2 `rental.damage.log` records created (one per serial) |
| **Result** | |

---

## 5. Stock Lot — Rental History

### TC-ST-015: Damage log count shows on serial form

| Field | Value |
|-------|-------|
| **Precondition** | SN001 has 2 damage logs |
| **Steps** | 1. Open SN001 lot form |
| **Expected** | `damage_count = 2`; smart button shows count |
| **Result** | |

### TC-ST-016: View damage logs from serial form

| Field | Value |
|-------|-------|
| **Precondition** | SN001 with damage logs |
| **Steps** | 1. Open SN001 lot form<br>2. Click damage log smart button |
| **Expected** | Damage log list filtered to SN001's logs |
| **Result** | |

---

## 6. Non-Serialized (Consumable) Products

### TC-ST-017: Consumable rental uses quantity without serial selection

| Field | Value |
|-------|-------|
| **Precondition** | Rental product with `tracking = 'none'` |
| **Steps** | 1. Open pickup wizard<br>2. Enter qty = 3<br>3. Validate |
| **Expected** | 3 units delivered; no serial selection required |
| **Result** | |

### TC-ST-018: Cancellation auto-returns consumable stock

| Field | Value |
|-------|-------|
| **Precondition** | 2 consumable units delivered; order not yet cancelled |
| **Steps** | 1. Click "Cancel" on order |
| **Expected** | Return stock move created and validated for 2 units; order cancelled |
| **Result** | |

### TC-ST-019: Cancellation does NOT auto-return serialized items

| Field | Value |
|-------|-------|
| **Precondition** | Serial-tracked units picked up; order not cancelled |
| **Steps** | 1. Click "Cancel" |
| **Expected** | Error or warning: must manually return serialized items before cancel |
| **Result** | |

---

## 7. Combo Products

### TC-ST-020: Combo rental — individual components tracked

| Field | Value |
|-------|-------|
| **Precondition** | Combo product containing 2 rental items (each with `rent_ok=True`) |
| **Steps** | 1. Add combo to rental order<br>2. Complete pickup |
| **Expected** | Each component tracked individually in stock; wizard excludes combo line itself |
| **Result** | |
