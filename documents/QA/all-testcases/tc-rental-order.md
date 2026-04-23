# Test Cases: Rental Order Lifecycle

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- At least 1 rental product configured with `rent_ok=True` and daily pricing
- Company rental settings configured (rental location exists)
- User logged in with Salesman or Manager role

---

## 1. Order Creation & Date Setup

### TC-RO-001: Create rental order from Rental menu

| Field | Value |
|-------|-------|
| **Precondition** | User has Salesman role |
| **Steps** | 1. Go to Rental > Orders > New<br>2. Add a rental product line<br>3. Save |
| **Expected** | Order created with `is_rental_order=True`, `rental_status=draft` |
| **Result** | |

### TC-RO-002: Auto-set dates on new order

| Field | Value |
|-------|-------|
| **Precondition** | New rental order (no dates set) |
| **Steps** | 1. Open Rental > Orders > New (do not set dates)<br>2. Observe `rental_start_date` and `rental_return_date` fields |
| **Expected** | `rental_start_date` ≈ now + 1 hr, `rental_return_date` ≈ now + 25 hrs |
| **Result** | |

### TC-RO-003: Invalid dates rejected (return ≤ start)

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft |
| **Steps** | 1. Set `return_date` equal to or earlier than `start_date`<br>2. Try to confirm or save |
| **Expected** | Validation error raised; order not saved/confirmed |
| **Result** | |

### TC-RO-004: Duration computed correctly — whole days

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft |
| **Steps** | 1. Set `start_date = 2026-05-01 09:00`<br>2. Set `return_date = 2026-05-03 09:00` |
| **Expected** | `duration_days = 2`, `remaining_hours = 0` |
| **Result** | |

### TC-RO-005: Duration computed correctly — days + hours

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft |
| **Steps** | 1. Set `start_date = 2026-05-01 09:00`<br>2. Set `return_date = 2026-05-03 14:00` |
| **Expected** | `duration_days = 2`, `remaining_hours = 5` |
| **Result** | |

---

## 2. Status Transitions

### TC-RO-006: Draft → Sent

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in draft with at least one product line |
| **Steps** | 1. Click "Send by Email" / "Send Quotation" |
| **Expected** | `rental_status = sent`; email wizard opens |
| **Result** | |

### TC-RO-007: Sent → Pickup (confirm order)

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in "sent" state |
| **Steps** | 1. Click "Confirm" |
| **Expected** | `rental_status = pickup`; delivery stock move created; `next_action_date = rental_start_date` |
| **Result** | |

### TC-RO-008: Pickup → Return after full pickup

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order, all items reserved |
| **Steps** | 1. Click "Pickup" button<br>2. Confirm all quantities in wizard<br>3. Click "Validate" |
| **Expected** | `rental_status = return`; `next_action_date = rental_return_date` |
| **Result** | |

### TC-RO-009: Return → Returned after full return

| Field | Value |
|-------|-------|
| **Precondition** | All items picked up |
| **Steps** | 1. Click "Return" button<br>2. Confirm all quantities in wizard<br>3. Click "Validate" |
| **Expected** | `rental_status = returned`; all lines show `qty_returned >= qty_delivered` |
| **Result** | |

### TC-RO-010: Partial pickup keeps status at "pickup"

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with 2 units ordered |
| **Steps** | 1. Click "Pickup"<br>2. Enter qty = 1 (partial)<br>3. Validate |
| **Expected** | `rental_status = pickup`; `has_pickable_lines = True` |
| **Result** | |

### TC-RO-011: Partial return keeps status at "return"

| Field | Value |
|-------|-------|
| **Precondition** | All 2 units picked up |
| **Steps** | 1. Click "Return"<br>2. Enter qty = 1 (partial)<br>3. Validate |
| **Expected** | `rental_status = return`; order still has returnable lines |
| **Result** | |

### TC-RO-012: Late detection — is_late flag

| Field | Value |
|-------|-------|
| **Precondition** | Order in "return" state; `rental_return_date` is in the past |
| **Steps** | 1. Check `is_late` field on order |
| **Expected** | `is_late = True`; late badge/color shown |
| **Result** | |

### TC-RO-013: Cancellation auto-returns consumable stock

| Field | Value |
|-------|-------|
| **Precondition** | Order confirmed; some consumable items already picked up |
| **Steps** | 1. Click "Cancel" |
| **Expected** | Auto-return stock move created for delivered consumable items; order cancelled |
| **Result** | |

---

## 3. Rental Completion Tracking

### TC-RO-014: Completion — all items returned

| Field | Value |
|-------|-------|
| **Precondition** | All items fully returned |
| **Steps** | 1. Check `rental_completion` field on order |
| **Expected** | Returns axis shows "Returned: X/X" |
| **Result** | |

### TC-RO-015: Completion — all invoices paid

| Field | Value |
|-------|-------|
| **Precondition** | All rental invoices in "paid" state |
| **Steps** | 1. Check `rental_completion` field |
| **Expected** | Paid axis shows "Paid: X/X" |
| **Result** | |

### TC-RO-016: Completion — deposit refunded

| Field | Value |
|-------|-------|
| **Precondition** | Deposit invoice paid and credit note (reversal) issued |
| **Steps** | 1. Check `rental_completion` field |
| **Expected** | Deposit refunded axis shows "Deposit refunded: 1/1" |
| **Result** | |

### TC-RO-017: Completion = complete when all 3 axes satisfied

| Field | Value |
|-------|-------|
| **Precondition** | All items returned, all invoices paid, deposit refunded |
| **Steps** | 1. Check `rental_completion` field |
| **Expected** | `rental_completion = complete`; badge shows complete |
| **Result** | |

### TC-RO-018: Completion = incomplete when any axis unsatisfied

| Field | Value |
|-------|-------|
| **Precondition** | All items returned but invoice unpaid |
| **Steps** | 1. Check `rental_completion` field |
| **Expected** | `rental_completion = incomplete` |
| **Result** | |

---

## 4. Price Recalculation

### TC-RO-019: Action update rental prices

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed rental order; dates changed |
| **Steps** | 1. Change `rental_return_date` to extend duration<br>2. Click "Update Prices" button |
| **Expected** | Line unit prices recalculated to match new duration |
| **Result** | |

### TC-RO-020: Changing dates in schedule view does not show warning

| Field | Value |
|-------|-------|
| **Precondition** | Rental order visible in Gantt/schedule view |
| **Steps** | 1. Drag rental line to extend duration in schedule view |
| **Expected** | Price updates silently (no "price changed" popup) |
| **Result** | |

---

## 5. Deposit Sync Check on Actions

### TC-RO-021: Confirm triggers deposit sync check

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with unsynced deposit lines |
| **Steps** | 1. Click "Confirm" |
| **Expected** | Deposit sync wizard opens showing mismatch info |
| **Result** | |

### TC-RO-022: Send quotation triggers deposit sync check

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with deposit mismatch |
| **Steps** | 1. Click "Send Quotation" |
| **Expected** | Deposit sync wizard opens before sending |
| **Result** | |

### TC-RO-023: Sync and continue — syncs then executes original action

| Field | Value |
|-------|-------|
| **Precondition** | Deposit sync wizard is open |
| **Steps** | 1. Click "Sync & Continue" in wizard |
| **Expected** | Deposits synced; original action (confirm/send) executed |
| **Result** | |

### TC-RO-024: Skip sync — continues without syncing

| Field | Value |
|-------|-------|
| **Precondition** | Deposit sync wizard is open |
| **Steps** | 1. Click "Continue as is" in wizard |
| **Expected** | Original action executed without syncing deposits |
| **Result** | |

---

## 6. Separate Subtotals Display

### TC-RO-025: Rental lines subtotal shown separately from deposit subtotal

| Field | Value |
|-------|-------|
| **Precondition** | Order with both rental lines and deposit line |
| **Steps** | 1. Open order form<br>2. Observe subtotal fields |
| **Expected** | `rental_lines_subtotal` shows sum of rental lines only; `deposit_lines_subtotal` shows deposit only |
| **Result** | |

---

## 7. Pickup Payment Requirement

### TC-RO-026: Pickup blocked if invoices unpaid (payment_before_pickup enabled)

| Field | Value |
|-------|-------|
| **Precondition** | Company setting `require_payment_before_pickup=True`; rental invoice not paid |
| **Steps** | 1. Try to click "Pickup" button |
| **Expected** | Error: "Please pay invoice before pickup" (or equivalent); pickup blocked |
| **Result** | |

### TC-RO-027: Pickup allowed if invoices paid

| Field | Value |
|-------|-------|
| **Precondition** | `require_payment_before_pickup=True`; rental invoice fully paid |
| **Steps** | 1. Click "Pickup" button |
| **Expected** | Pickup wizard opens normally |
| **Result** | |

### TC-RO-028: Pickup allowed when payment_before_pickup disabled

| Field | Value |
|-------|-------|
| **Precondition** | `require_payment_before_pickup=False`; invoice not paid |
| **Steps** | 1. Click "Pickup" button |
| **Expected** | Pickup wizard opens; no payment check |
| **Result** | |

---

## 8. Invoicing

### TC-RO-029: Create invoice from rental order

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed rental order with rental lines |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | Invoice(s) created; order linked to invoice(s) |
| **Result** | |

### TC-RO-030: Auto-post invoice if company setting enabled

| Field | Value |
|-------|-------|
| **Precondition** | `company.auto_confirm_invoice=True` |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | Invoice automatically confirmed (state = posted) |
| **Result** | |
