# Test Cases: Deposit Handling

> Module: `ggg_rental` | Phase: 1 | Last updated: 2026-04-06

## Preconditions

- Deposit product configured: service product with `is_rental_deposit=True`
- At least 1 rental product with pricing
- Company settings: deposit_auto_refund configured

---

## 1. Deposit Product Setup

### TC-DP-001: Mark product as deposit

| Field | Value |
|-------|-------|
| **Precondition** | Service product exists |
| **Steps** | 1. Open product form<br>2. Set is_rental_deposit=True<br>3. Save |
| **Expected** | Product is recognized as a deposit product when added to rental orders |
| **Result** | |

---

## 2. Split Invoicing

### TC-DP-002: Mixed order creates two invoices

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with rental product lines + deposit line |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | 2 invoices created: one for deposit only, one for rental lines only |
| **Result** | |

### TC-DP-003: Rental-only order creates single invoice

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with only rental lines (no deposit) |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | 1 invoice created with all rental lines |
| **Result** | |

### TC-DP-004: Deposit-only order creates single invoice

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with only a deposit line |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | 1 invoice created with deposit line only |
| **Result** | |

---

## 3. Deposit Credit Note on Return

### TC-DP-005: Full return — full deposit refund

| Field | Value |
|-------|-------|
| **Precondition** | Order with deposit=1000 THB (invoiced and paid), all items picked up |
| **Steps** | 1. Return all items via return wizard |
| **Expected** | Credit note created for 1000 THB linked to original deposit invoice |
| **Result** | |

### TC-DP-006: Partial return — proportional deposit refund

| Field | Value |
|-------|-------|
| **Precondition** | Order with deposit=1000 THB, 5 items picked up |
| **Steps** | 1. Return 3 of 5 items via return wizard |
| **Expected** | Credit note created for 600 THB (3/5 × 1000) |
| **Result** | |

### TC-DP-007: Second partial return — additional credit note

| Field | Value |
|-------|-------|
| **Precondition** | First return: 3/5 items returned (credit note 600 THB created) |
| **Steps** | 1. Return remaining 2 items via return wizard |
| **Expected** | Second credit note for 400 THB (2/5 × 1000). Total refunded = 1000 THB |
| **Result** | |

---

## 4. Auto-Refund Setting

### TC-DP-008: Auto-refund enabled

| Field | Value |
|-------|-------|
| **Precondition** | company.deposit_auto_refund=True, deposit invoiced and paid |
| **Steps** | 1. Return items (triggers deposit credit note) |
| **Expected** | Credit note created AND payment automatically registered on the credit note |
| **Result** | |

### TC-DP-009: Auto-refund disabled

| Field | Value |
|-------|-------|
| **Precondition** | company.deposit_auto_refund=False, deposit invoiced and paid |
| **Steps** | 1. Return items (triggers deposit credit note) |
| **Expected** | Credit note created but NO payment registered (staff must process manually) |
| **Result** | |

### TC-DP-010: Configure auto-refund in settings

| Field | Value |
|-------|-------|
| **Precondition** | Admin access |
| **Steps** | 1. Go to Rental > Configuration > Settings<br>2. Toggle "Auto Refund Deposit"<br>3. Save |
| **Expected** | Setting saved, applies to subsequent returns |
| **Result** | |
