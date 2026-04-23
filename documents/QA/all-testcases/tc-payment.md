# Test Cases: Payment Processing

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Rental order with invoices created and posted
- Payment journals configured (cash, bank, credit card)
- Users: cashier role available

---

## 1. Payment Fields

### TC-PM-001: Payment stores cashier_id

| Field | Value |
|-------|-------|
| **Precondition** | User "Alice" registers payment |
| **Steps** | 1. Register payment on rental invoice |
| **Expected** | `cashier_id = Alice` on payment record |
| **Result** | |

### TC-PM-002: cashier_id defaults to current user

| Field | Value |
|-------|-------|
| **Precondition** | User "Bob" is logged in |
| **Steps** | 1. Open payment register wizard |
| **Expected** | `cashier_id = Bob` pre-populated |
| **Result** | |

### TC-PM-003: payment_reference_2 stores secondary reference

| Field | Value |
|-------|-------|
| **Precondition** | Payment for EDC or 2c2p transaction |
| **Steps** | 1. Register payment<br>2. Enter `payment_reference_2 = "EDC-9987"` |
| **Expected** | `payment_reference_2 = "EDC-9987"` stored on payment |
| **Result** | |

### TC-PM-004: approval_code stored on payment

| Field | Value |
|-------|-------|
| **Precondition** | Credit card payment with approval code |
| **Steps** | 1. Register payment; enter `approval_code = "APV123456"` |
| **Expected** | `approval_code = "APV123456"` saved |
| **Result** | |

### TC-PM-005: display_method computed from payment method line

| Field | Value |
|-------|-------|
| **Precondition** | Payment via "Cash" journal |
| **Steps** | 1. Register payment via Cash<br>2. Check `display_method` field |
| **Expected** | `display_method = "Cash"` (or journal method name) |
| **Result** | |

---

## 2. Rental Payment Flag

### TC-PM-006: is_rental_payment = True for rental invoice payments

| Field | Value |
|-------|-------|
| **Precondition** | Payment reconciled to rental invoice |
| **Steps** | 1. Check `is_rental_payment` on payment |
| **Expected** | `is_rental_payment = True` |
| **Result** | |

### TC-PM-007: is_rental_payment = False for non-rental invoice payments

| Field | Value |
|-------|-------|
| **Precondition** | Payment for a regular (non-rental) invoice |
| **Steps** | 1. Check `is_rental_payment` |
| **Expected** | `is_rental_payment = False` |
| **Result** | |

---

## 3. Payment Register Wizard

### TC-PM-008: Wizard copies references to payment

| Field | Value |
|-------|-------|
| **Precondition** | Payment register wizard open |
| **Steps** | 1. Enter `payment_reference = "REF001"`, `payment_reference_2 = "EDC-001"`, `approval_code = "APV001"`<br>2. Create payment |
| **Expected** | All reference fields copied to created payment record |
| **Result** | |

### TC-PM-009: Wizard blocked if cashier has confirmed reconciliation for that date

| Field | Value |
|-------|-------|
| **Precondition** | Cashier "Alice" has confirmed reconciliation for 2026-05-01 |
| **Steps** | 1. Alice tries to register payment dated 2026-05-01 |
| **Expected** | Error: "Reconciliation already confirmed for this date" |
| **Result** | |

---

## 4. Reconciliation Lock on Payments

### TC-PM-010: Cannot create payment if cashier date is confirmed

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed daily reconciliation for cashier/date combo |
| **Steps** | 1. Try to create new payment with same cashier and date |
| **Expected** | Error raised; payment not created |
| **Result** | |

### TC-PM-011: Cannot edit payment amount in confirmed reconciliation

| Field | Value |
|-------|-------|
| **Precondition** | Payment linked to a confirmed reconciliation |
| **Steps** | 1. Try to change `amount` on the payment |
| **Expected** | Error raised; payment not modified |
| **Result** | |

### TC-PM-012: Cannot delete payment in confirmed reconciliation

| Field | Value |
|-------|-------|
| **Precondition** | Payment in a confirmed reconciliation |
| **Steps** | 1. Try to delete the payment |
| **Expected** | Error raised; payment not deleted |
| **Result** | |

### TC-PM-013: Can edit payment in draft reconciliation

| Field | Value |
|-------|-------|
| **Precondition** | Payment in draft (unconfirmed) reconciliation |
| **Steps** | 1. Edit payment fields |
| **Expected** | Edit succeeds |
| **Result** | |

---

## 5. Completion Tracking Trigger

### TC-PM-014: Invoice payment state change triggers completion recompute

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with invoice |
| **Steps** | 1. Pay rental invoice in full |
| **Expected** | `rental_completion` recomputed; "Paid" axis updates |
| **Result** | |

### TC-PM-015: Partial payment does not mark invoice as paid

| Field | Value |
|-------|-------|
| **Precondition** | Invoice for 10,000; pay 5,000 |
| **Steps** | 1. Register partial payment of 5,000 |
| **Expected** | Invoice state = "in_payment" or "partial"; completion not fully met |
| **Result** | |

---

## 6. Thai Invoice

### TC-PM-016: Thai words shown for THB invoices

| Field | Value |
|-------|-------|
| **Precondition** | Company currency = THB; invoice total = 12,500 |
| **Steps** | 1. Print invoice report |
| **Expected** | Amount in Thai words: "หนึ่งหมื่นสองพันห้าร้อยบาทถ้วน" (or equivalent) |
| **Result** | |

### TC-PM-017: Thai words not shown for non-THB invoices

| Field | Value |
|-------|-------|
| **Precondition** | Invoice currency = USD |
| **Steps** | 1. Print invoice report |
| **Expected** | No Thai word amount (or fallback to standard) |
| **Result** | |

### TC-PM-018: Invoice uses GGG rental report template

| Field | Value |
|-------|-------|
| **Precondition** | Rental invoice posted |
| **Steps** | 1. Print invoice |
| **Expected** | Report uses `ggg_rental.ggg_report_invoice_document` template |
| **Result** | |

---

## 7. Payment with Auto-Confirm Invoice

### TC-PM-019: Invoice auto-confirmed on create when setting enabled

| Field | Value |
|-------|-------|
| **Precondition** | `company.auto_confirm_invoice = True` |
| **Steps** | 1. Create invoice from rental order |
| **Expected** | Invoice state = "posted" immediately (no manual confirm needed) |
| **Result** | |

### TC-PM-020: Invoice stays draft when auto-confirm disabled

| Field | Value |
|-------|-------|
| **Precondition** | `company.auto_confirm_invoice = False` |
| **Steps** | 1. Create invoice from rental order |
| **Expected** | Invoice state = "draft"; requires manual confirmation |
| **Result** | |
