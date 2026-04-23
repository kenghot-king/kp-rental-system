# Test Cases: Daily Reconciliation

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Payments exist in the system in posted state
- Cashier users configured
- User with `group_rental_supervisor` role available for confirm/reopen

---

## 1. Reconciliation Creation

### TC-RC-001: Create daily reconciliation from "Needed" view

| Field | Value |
|-------|-------|
| **Precondition** | Unreconciled payments exist for cashier "Alice" on 2026-05-01 |
| **Steps** | 1. Go to Rental > Reconciliation > Reconciliation Needed<br>2. Find Alice's row<br>3. Click "Create Reconciliation" |
| **Expected** | New `rental.daily.reconciliation` created for Alice on 2026-05-01 |
| **Result** | |

### TC-RC-002: Uniqueness — one reconciliation per cashier per date

| Field | Value |
|-------|-------|
| **Precondition** | Reconciliation already exists for Alice on 2026-05-01 |
| **Steps** | 1. Try to create another reconciliation for same cashier + date |
| **Expected** | Error: unique constraint violation |
| **Result** | |

### TC-RC-003: Create reconciliation opens existing if already exists

| Field | Value |
|-------|-------|
| **Precondition** | Reconciliation already exists for Alice/2026-05-01 |
| **Steps** | 1. Click "Create Reconciliation" from Needed view for Alice/2026-05-01 |
| **Expected** | Opens existing draft reconciliation (no duplicate created) |
| **Result** | |

---

## 2. Line Rebuilding

### TC-RC-004: Rebuild lines groups payments by method and journal

| Field | Value |
|-------|-------|
| **Precondition** | 3 payments: 2 × Cash (Journal A), 1 × Credit Card (Journal B) |
| **Steps** | 1. Open draft reconciliation<br>2. Click "Rebuild Lines" (or auto-rebuilt) |
| **Expected** | 2 reconciliation lines: (Cash, Journal A) and (Credit Card, Journal B) |
| **Result** | |

### TC-RC-005: Rebuild updates expected_amount from payments

| Field | Value |
|-------|-------|
| **Precondition** | Cash payments: 1,000 + 2,000 = 3,000 |
| **Steps** | 1. Rebuild lines |
| **Expected** | Cash line `expected_amount = 3,000` |
| **Result** | |

### TC-RC-006: Rebuild excludes payments from other cashiers

| Field | Value |
|-------|-------|
| **Precondition** | Payments by Alice and Bob on same date |
| **Steps** | 1. Open Alice's reconciliation; rebuild |
| **Expected** | Only Alice's payments included |
| **Result** | |

### TC-RC-007: Rebuild excludes payments already in other confirmed reconciliations

| Field | Value |
|-------|-------|
| **Precondition** | Payment P1 belongs to another confirmed reconciliation |
| **Steps** | 1. Rebuild Alice's new reconciliation |
| **Expected** | P1 not included in new reconciliation lines |
| **Result** | |

### TC-RC-008: Rebuild clears old lines before recreating

| Field | Value |
|-------|-------|
| **Precondition** | Reconciliation with existing lines; payment added later |
| **Steps** | 1. Rebuild lines |
| **Expected** | Old lines removed; new lines created fresh with all current payments |
| **Result** | |

---

## 3. Entering Actual Amounts

### TC-RC-009: Enter actual_amount on a line

| Field | Value |
|-------|-------|
| **Precondition** | Draft reconciliation with lines |
| **Steps** | 1. Find Cash line with expected = 3,000<br>2. Enter `actual_amount = 3,000`<br>3. Save |
| **Expected** | `actual_entered = True`; `variance = 0` |
| **Result** | |

### TC-RC-010: Variance = actual - expected

| Field | Value |
|-------|-------|
| **Precondition** | Expected = 3,000; enter actual = 2,800 |
| **Steps** | 1. Enter `actual_amount = 2,800` |
| **Expected** | `variance = -200` |
| **Result** | |

### TC-RC-011: actual_entered auto-set when actual_amount entered

| Field | Value |
|-------|-------|
| **Precondition** | Line with `actual_entered = False` |
| **Steps** | 1. Enter any value in `actual_amount` |
| **Expected** | `actual_entered = True` automatically |
| **Result** | |

---

## 4. Confirm Action

### TC-RC-012: Cannot confirm if any line missing actual_amount

| Field | Value |
|-------|-------|
| **Precondition** | 2 lines; only 1 has actual_amount entered |
| **Steps** | 1. Click "Confirm" |
| **Expected** | Error: all lines must have actual amount entered |
| **Result** | |

### TC-RC-013: Confirm with all actual amounts entered

| Field | Value |
|-------|-------|
| **Precondition** | All lines have actual_amount |
| **Steps** | 1. Click "Confirm" |
| **Expected** | `state = confirmed`; `confirmed_by = current user`; `confirmed_at = now` |
| **Result** | |

### TC-RC-014: Confirm links reconciliation_id to payments

| Field | Value |
|-------|-------|
| **Precondition** | Reconciliation confirmed |
| **Steps** | 1. Check payments linked to this reconciliation |
| **Expected** | Each payment has `reconciliation_id = this reconciliation` |
| **Result** | |

### TC-RC-015: Confirm requires supervisor role

| Field | Value |
|-------|-------|
| **Precondition** | User is a cashier without supervisor role |
| **Steps** | 1. Try to click "Confirm" |
| **Expected** | Access error or button hidden |
| **Result** | |

---

## 5. Reopen Action

### TC-RC-016: Reopen confirmed reconciliation → draft

| Field | Value |
|-------|-------|
| **Precondition** | Reconciliation in `confirmed` state |
| **Steps** | 1. Click "Reopen" (supervisor) |
| **Expected** | `state = draft`; `reopened_by = current user`; `reopened_at = now` |
| **Result** | |

### TC-RC-017: Reopen clears reconciliation_id from payments

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed reconciliation with linked payments |
| **Steps** | 1. Reopen reconciliation |
| **Expected** | All previously linked payments have `reconciliation_id = False` |
| **Result** | |

### TC-RC-018: Reopen requires supervisor role

| Field | Value |
|-------|-------|
| **Precondition** | Non-supervisor user |
| **Steps** | 1. Try to click "Reopen" |
| **Expected** | Access error or button hidden |
| **Result** | |

---

## 6. Multi-Confirm

### TC-RC-019: Bulk confirm multiple draft reconciliations

| Field | Value |
|-------|-------|
| **Precondition** | 3 draft reconciliations with all actual amounts entered |
| **Steps** | 1. Select all 3 in list view<br>2. Action > Confirm |
| **Expected** | All 3 confirmed; state = confirmed |
| **Result** | |

### TC-RC-020: Bulk confirm fails if any reconciliation has incomplete amounts

| Field | Value |
|-------|-------|
| **Precondition** | 3 reconciliations; 1 has missing actual_amount |
| **Steps** | 1. Bulk confirm all 3 |
| **Expected** | Error: one or more reconciliations have incomplete amounts; none confirmed |
| **Result** | |

---

## 7. Totals

### TC-RC-021: expected_total = sum of all line expected amounts

| Field | Value |
|-------|-------|
| **Precondition** | 2 lines: expected 3,000 + 2,000 |
| **Steps** | 1. Check `expected_total` on reconciliation |
| **Expected** | `expected_total = 5,000` |
| **Result** | |

### TC-RC-022: actual_total = sum of all line actual amounts

| Field | Value |
|-------|-------|
| **Precondition** | Actual: 3,000 + 1,800 |
| **Steps** | 1. Check `actual_total` |
| **Expected** | `actual_total = 4,800` |
| **Result** | |

### TC-RC-023: variance_total = actual_total - expected_total

| Field | Value |
|-------|-------|
| **Precondition** | Expected = 5,000; actual = 4,800 |
| **Steps** | 1. Check `variance_total` |
| **Expected** | `variance_total = -200` |
| **Result** | |

---

## 8. Reconciliation Reports

### TC-RC-024: Print PDF report for single reconciliation

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed reconciliation |
| **Steps** | 1. Click "Print PDF" button |
| **Expected** | PDF generated with date, cashier, method, journal, expected, actual, variance |
| **Result** | |

### TC-RC-025: Export XLSX for reconciliation

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed reconciliation |
| **Steps** | 1. Click "Export XLSX" button |
| **Expected** | XLSX downloaded with columns: Date, Cashier, State, Method, Journal, Expected, Actual, Variance, TOTAL |
| **Result** | |
