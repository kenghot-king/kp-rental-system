# Test Cases: Reporting, Views & Access Control

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- Multiple rental orders in various statuses (draft, pickup, return, returned)
- Multiple products, salespersons, and customers
- Test users: Salesman, Manager, System Admin

---

## 1. Rental Analysis Report

### TC-RP-001: Report shows daily breakdown

| Field | Value |
|-------|-------|
| **Precondition** | Order with 3-day rental for 2 units at 600 THB total |
| **Steps** | 1. Go to Rental > Reporting > Rental Analysis<br>2. Switch to list view |
| **Expected** | 3 rows (one per day), each with quantity ≈ 0.67, price = 200 |
| **Result** | |

### TC-RP-002: Group by product

| Field | Value |
|-------|-------|
| **Precondition** | Multiple rental orders for different products |
| **Steps** | 1. Open Rental Analysis<br>2. Switch to pivot view<br>3. Group rows by Product |
| **Expected** | Products grouped with summed quantities and prices |
| **Result** | |

### TC-RP-003: Group by salesperson

| Field | Value |
|-------|-------|
| **Precondition** | Orders assigned to different salespersons |
| **Steps** | 1. Open Rental Analysis<br>2. Group by Salesperson |
| **Expected** | Each salesperson shows their rental totals |
| **Result** | |

### TC-RP-004: Filter by date range

| Field | Value |
|-------|-------|
| **Precondition** | Orders spanning multiple months |
| **Steps** | 1. Open Rental Analysis<br>2. Add filter: Date between 2026-04-01 and 2026-04-30 |
| **Expected** | Only rental days within April 2026 shown |
| **Result** | |

### TC-RP-005: Graph view displays correctly

| Field | Value |
|-------|-------|
| **Precondition** | Rental data exists |
| **Steps** | 1. Open Rental Analysis<br>2. Switch to graph view |
| **Expected** | Line chart shows rental revenue over time |
| **Result** | |

---

## 2. Schedule (Gantt) View

### TC-RP-006: Gantt shows all active rentals

| Field | Value |
|-------|-------|
| **Precondition** | Multiple confirmed rental orders |
| **Steps** | 1. Go to Rental > Schedule |
| **Expected** | All confirmed order lines appear as bars from start_date to return_date |
| **Result** | |

### TC-RP-007: Color coding by status

| Field | Value |
|-------|-------|
| **Precondition** | Orders in various statuses (on-time, late, returned) |
| **Steps** | 1. View Gantt chart with mixed-status orders |
| **Expected** | Bars color-coded: blue=on-time pickup, red=late pickup, green=on-time return, orange=late return, gray=returned |
| **Result** | |

### TC-RP-008: Drag to reschedule

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order visible on Gantt |
| **Steps** | 1. Drag a Gantt bar to new dates |
| **Expected** | Rental dates update and line prices recalculate |
| **Result** | |

### TC-RP-009: Group by product

| Field | Value |
|-------|-------|
| **Precondition** | Multiple products on Gantt |
| **Steps** | 1. Group Gantt by Product |
| **Expected** | Each product row shows its rental order lines |
| **Result** | |

---

## 3. List View & Product Catalog

### TC-RP-010: List view shows rental status badges

| Field | Value |
|-------|-------|
| **Precondition** | Multiple rental orders |
| **Steps** | 1. Go to Rental > Orders |
| **Expected** | Each order shows colored status badge: draft=info, pickup=success, return=warning |
| **Result** | |

### TC-RP-011: Next action date shown

| Field | Value |
|-------|-------|
| **Precondition** | Order with rental_status=pickup |
| **Steps** | 1. View order list |
| **Expected** | Next action date column shows rental_start_date with remaining days widget |
| **Result** | |

### TC-RP-012: Product shows qty in rent

| Field | Value |
|-------|-------|
| **Precondition** | 5 units currently rented out |
| **Steps** | 1. Go to Rental > Products<br>2. Open product form |
| **Expected** | qty_in_rent = 5 |
| **Result** | |

### TC-RP-013: Product shows display price

| Field | Value |
|-------|-------|
| **Precondition** | Product with pricing 100 THB/day |
| **Steps** | 1. Go to Rental > Products<br>2. View product list |
| **Expected** | Shows "100.00 THB / 1 Day" |
| **Result** | |

---

## 4. Access Control

### TC-RP-014: Salesman can create orders

| Field | Value |
|-------|-------|
| **Precondition** | Logged in as user with Salesman group |
| **Steps** | 1. Go to Rental > Orders<br>2. Create a new order |
| **Expected** | User can create, read, and edit rental orders |
| **Result** | |

### TC-RP-015: Salesman cannot delete damage logs

| Field | Value |
|-------|-------|
| **Precondition** | Logged in as Salesman, existing damage log record |
| **Steps** | 1. Navigate to damage log list<br>2. Try to delete a record |
| **Expected** | System denies the operation (Access Error) |
| **Result** | |

### TC-RP-016: Manager can access reporting

| Field | Value |
|-------|-------|
| **Precondition** | Logged in as Manager |
| **Steps** | 1. Go to Rental > Reporting > Rental Analysis |
| **Expected** | Report is accessible and displays data |
| **Result** | |

### TC-RP-017: Settings restricted to system admin

| Field | Value |
|-------|-------|
| **Precondition** | Logged in as Manager (NOT System Admin) |
| **Steps** | 1. Try to access Rental > Configuration > Settings |
| **Expected** | Settings page is not accessible (menu hidden or access denied) |
| **Result** | |
