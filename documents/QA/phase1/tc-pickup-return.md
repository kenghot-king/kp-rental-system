# Test Cases: Pickup & Return Wizard

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- 2 rental products: 1 non-tracked (bulk), 1 serial-tracked (`tracking=serial`)
- Serial-tracked product has at least 5 serial numbers in stock (SN001–SN005)
- Company rental settings configured
- Confirmed rental order with lines for both products

---

## 1. Bulk Product Pickup

### TC-PK-001: Full pickup of bulk product

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with 5 units of non-tracked product |
| **Steps** | 1. Click "Pickup"<br>2. Wizard shows qty_delivered = 5<br>3. Click "Validate" |
| **Expected** | qty_delivered=5, delivery move validated, rental_status = "return" |
| **Result** | |

### TC-PK-002: Partial pickup of bulk product

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with 5 units |
| **Steps** | 1. Click "Pickup"<br>2. Change qty_delivered to 3<br>3. Validate |
| **Expected** | qty_delivered=3, rental_status remains "pickup", Pickup button still visible |
| **Result** | |

### TC-PK-003: Pickup more than reserved auto-increases reserved

| Field | Value |
|-------|-------|
| **Precondition** | Order with 3 units reserved |
| **Steps** | 1. Click "Pickup"<br>2. Set qty_delivered = 5<br>3. Validate |
| **Expected** | product_uom_qty auto-increases to 5, qty_delivered=5 |
| **Result** | |

---

## 2. Serial-Tracked Product Pickup

### TC-PK-004: Select serials from available stock

| Field | Value |
|-------|-------|
| **Precondition** | Order with serial-tracked product, 3 reserved |
| **Steps** | 1. Click "Pickup"<br>2. Check pickeable_lot_ids column |
| **Expected** | Shows available serial numbers from warehouse stock |
| **Result** | |

### TC-PK-005: Pick specific serials

| Field | Value |
|-------|-------|
| **Precondition** | Pickup wizard open with serial-tracked product |
| **Steps** | 1. Select SN001 and SN002 from pickeable_lot_ids |
| **Expected** | qty_delivered auto-computes to 2, pickedup_lot_ids = {SN001, SN002} |
| **Result** | |

### TC-PK-006: Serials assigned to stock move

| Field | Value |
|-------|-------|
| **Precondition** | Serials selected in pickup wizard |
| **Steps** | 1. Click "Validate"<br>2. Check delivery stock move lines |
| **Expected** | Move lines have correct lot_id for each serial, move state = "done" |
| **Result** | |

### TC-PK-007: Pickup logged in chatter

| Field | Value |
|-------|-------|
| **Precondition** | Pickup wizard completed |
| **Steps** | 1. Check order chatter after pickup |
| **Expected** | Message posted with product name, quantity picked, serial numbers (if applicable) |
| **Result** | |

---

## 3. Bulk Product Return

### TC-RT-001: Full return of bulk product

| Field | Value |
|-------|-------|
| **Precondition** | Order with 5 picked-up units of non-tracked product |
| **Steps** | 1. Click "Return"<br>2. Confirm qty_returned = 5<br>3. Validate |
| **Expected** | qty_returned=5, return stock move created and validated, rental_status = "returned" |
| **Result** | |

### TC-RT-002: Partial return of bulk product

| Field | Value |
|-------|-------|
| **Precondition** | Order with 5 picked-up units |
| **Steps** | 1. Click "Return"<br>2. Set qty_returned = 2<br>3. Validate |
| **Expected** | qty_returned=2, rental_status remains "return" |
| **Result** | |

### TC-RT-003: Cannot return more than picked up

| Field | Value |
|-------|-------|
| **Precondition** | Order with 3 picked-up units |
| **Steps** | 1. Click "Return"<br>2. Set qty_returned = 5<br>3. Try to validate |
| **Expected** | Validation error: cannot return more than picked up |
| **Result** | |

---

## 4. Serial-Tracked Product Return

### TC-RT-004: Returnable serials shown

| Field | Value |
|-------|-------|
| **Precondition** | Order with 3 serials picked up (SN001, SN002, SN003) |
| **Steps** | 1. Click "Return"<br>2. Check returnable_lot_ids column |
| **Expected** | Shows SN001, SN002, SN003 |
| **Result** | |

### TC-RT-005: Return specific serials

| Field | Value |
|-------|-------|
| **Precondition** | Return wizard open with serial-tracked product |
| **Steps** | 1. Select SN001 and SN002 from returnable_lot_ids |
| **Expected** | qty_returned auto-computes to 2, returned_lot_ids = {SN001, SN002} |
| **Result** | |

### TC-RT-006: Second return shows remaining serials only

| Field | Value |
|-------|-------|
| **Precondition** | SN001 and SN002 already returned from previous return |
| **Steps** | 1. Click "Return" again<br>2. Check returnable_lot_ids |
| **Expected** | Only SN003 is shown |
| **Result** | |

### TC-RT-007: Return serial assigned to return stock move

| Field | Value |
|-------|-------|
| **Precondition** | Serials selected in return wizard |
| **Steps** | 1. Validate<br>2. Check return stock move lines |
| **Expected** | Return move lines have correct lot_id, move state = "done", items back in warehouse |
| **Result** | |

### TC-RT-008: Return logged in chatter

| Field | Value |
|-------|-------|
| **Precondition** | Return wizard completed |
| **Steps** | 1. Check order chatter after return |
| **Expected** | Message posted with product name, quantity returned, condition, serial numbers |
| **Result** | |
