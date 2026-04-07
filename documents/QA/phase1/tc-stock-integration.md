# Test Cases: Stock Integration

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- Rental products with stock available in warehouse
- Serial-tracked product with serial numbers in stock
- Company rental location configured (auto-created)
- User with Stock User group for stock move visibility

---

## 1. Delivery Move & Rental Location

### TC-ST-001: Delivery move created on confirm

| Field | Value |
|-------|-------|
| **Precondition** | Draft rental order with product lines |
| **Steps** | 1. Confirm the rental order |
| **Expected** | Stock move created: source=WH/Stock, destination=Rental location, product and qty matching SO line |
| **Result** | |

### TC-ST-002: Rental location auto-created per company

| Field | Value |
|-------|-------|
| **Precondition** | Multi-company environment or new company |
| **Steps** | 1. Create a new company<br>2. Check stock locations |
| **Expected** | "Rental" internal location auto-created under Customers location for the new company |
| **Result** | |

---

## 2. Pickup Stock Validation

### TC-ST-003: Pickup validates delivery move

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with reserved items |
| **Steps** | 1. Open pickup wizard<br>2. Confirm all quantities<br>3. Validate |
| **Expected** | Delivery stock move state changes to "done" |
| **Result** | |

### TC-ST-004: Serial numbers assigned to move lines

| Field | Value |
|-------|-------|
| **Precondition** | Serial-tracked product, serials selected in pickup wizard |
| **Steps** | 1. Select specific serials in pickup wizard<br>2. Validate<br>3. Check stock move lines |
| **Expected** | Each move line has correct lot_id assignment |
| **Result** | |

---

## 3. Return Stock Moves

### TC-ST-005: Return move created and validated

| Field | Value |
|-------|-------|
| **Precondition** | Order with items picked up |
| **Steps** | 1. Open return wizard<br>2. Confirm quantities<br>3. Validate |
| **Expected** | New stock move: source=Rental location, destination=WH/Stock, state="done" |
| **Result** | |

### TC-ST-006: Return serials assigned to return move

| Field | Value |
|-------|-------|
| **Precondition** | Serial-tracked products, serials selected in return wizard |
| **Steps** | 1. Select serials to return<br>2. Validate<br>3. Check return stock move lines |
| **Expected** | Return move lines have correct lot_id for each returned serial |
| **Result** | |

### TC-ST-007: Stock restored after return

| Field | Value |
|-------|-------|
| **Precondition** | All items returned |
| **Steps** | 1. Check product stock levels after return |
| **Expected** | Product qty available in warehouse increases by returned quantity |
| **Result** | |

---

## 4. Stock Move Visibility & Qty in Rent

### TC-ST-008: Stock move count displayed

| Field | Value |
|-------|-------|
| **Precondition** | Order with 1 delivery + 1 return move completed |
| **Steps** | 1. Open rental order form |
| **Expected** | "Stock Moves (2)" button visible on order form |
| **Result** | |

### TC-ST-009: View stock moves from order

| Field | Value |
|-------|-------|
| **Precondition** | Order with stock moves |
| **Steps** | 1. Click "Stock Moves" button on order |
| **Expected** | List view shows all delivery and return moves for this order |
| **Result** | |

### TC-ST-010: Qty in rent increases on pickup

| Field | Value |
|-------|-------|
| **Precondition** | Product with qty_in_rent=0 |
| **Steps** | 1. Create and confirm rental order for 3 units<br>2. Pick up all 3 units<br>3. Check product form |
| **Expected** | product.qty_in_rent = 3 |
| **Result** | |

### TC-ST-011: Qty in rent decreases on return

| Field | Value |
|-------|-------|
| **Precondition** | Product with 3 units currently rented |
| **Steps** | 1. Return 2 units<br>2. Check product form |
| **Expected** | product.qty_in_rent = 1 (still 1 in rent) |
| **Result** | |
