# Test Cases: Deposit Management

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Deposit product configured: service product with `is_rental_deposit=True`
- At least 1 rental product with pricing and `deposit_price` set
- Company settings: `deposit_auto_refund` configured

---

## 1. Deposit Product Setup

### TC-DP-001: Mark product as deposit product

| Field | Value |
|-------|-------|
| **Precondition** | Service product exists |
| **Steps** | 1. Open product form<br>2. Set `is_rental_deposit=True`<br>3. Save |
| **Expected** | Product marked as deposit; excluded from regular rental line calculations |
| **Result** | |

### TC-DP-002: Set deposit_price on rental product

| Field | Value |
|-------|-------|
| **Precondition** | Rental product with `rent_ok=True` |
| **Steps** | 1. Open product form > Rental tab<br>2. Set `deposit_price = 5,000`<br>3. Save |
| **Expected** | `deposit_price` saved as company-dependent field |
| **Result** | |

---

## 2. Deposit Sync

### TC-DP-003: Sync deposits auto-creates deposit line

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with product having `deposit_price > 0`; no deposit line yet |
| **Steps** | 1. Click "Sync Deposits" button on order |
| **Expected** | Deposit line created linked to rental line via `deposit_parent_id`; price = `deposit_price × qty` |
| **Result** | |

### TC-DP-004: Sync deposits updates existing deposit line on qty change

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with deposit line; qty changed to 3 |
| **Steps** | 1. Click "Sync Deposits" |
| **Expected** | Deposit line qty updated to 3; total = `deposit_price × 3` |
| **Result** | |

### TC-DP-005: Sync deposits removes orphan deposit lines

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with deposit line; rental line deleted |
| **Steps** | 1. Delete rental line<br>2. Click "Sync Deposits" |
| **Expected** | Orphan deposit line removed |
| **Result** | |

### TC-DP-006: Sync deposits — no deposit_price means no deposit line

| Field | Value |
|-------|-------|
| **Precondition** | Rental product with `deposit_price = 0` |
| **Steps** | 1. Add product to order<br>2. Click "Sync Deposits" |
| **Expected** | No deposit line created |
| **Result** | |

---

## 3. Split Invoicing

### TC-DP-007: Order with rental + deposit lines creates two invoices

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with 1 rental line + 1 deposit line |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | 2 invoices created: one for deposit only, one for rental lines only |
| **Result** | |

### TC-DP-008: Rental-only order creates single invoice

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with only rental lines |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | 1 invoice created with all rental lines |
| **Result** | |

### TC-DP-009: Deposit-only line creates deposit invoice

| Field | Value |
|-------|-------|
| **Precondition** | Confirmed order with only a deposit line (no rental lines) |
| **Steps** | 1. Click "Create Invoice" |
| **Expected** | 1 invoice created with deposit line |
| **Result** | |

### TC-DP-010: Re-invoicing after credit note does not duplicate deposit invoice

| Field | Value |
|-------|-------|
| **Precondition** | Deposit invoice paid; credit note (reversal) issued |
| **Steps** | 1. Try to create invoice again |
| **Expected** | System skips re-creating deposit invoice (already-invoiced guard); only creates for uninvoiced lines |
| **Result** | |

---

## 4. Deposit Credit Note on Return

### TC-DP-011: Full return — full deposit refund

| Field | Value |
|-------|-------|
| **Precondition** | 2 units delivered; deposit invoice paid; `deposit_auto_refund=False` |
| **Steps** | 1. Return all 2 units in wizard<br>2. Observe deposit credit note |
| **Expected** | Credit note for 100% of deposit amount created |
| **Result** | |

### TC-DP-012: Partial return — proportional deposit refund

| Field | Value |
|-------|-------|
| **Precondition** | 2 units delivered; deposit invoice paid |
| **Steps** | 1. Return 1 unit |
| **Expected** | Credit note for 50% (1/2) of deposit created |
| **Result** | |

### TC-DP-013: Second partial return — remaining deposit refunded

| Field | Value |
|-------|-------|
| **Precondition** | 1st partial return gave 50% credit note; 1 unit still out |
| **Steps** | 1. Return remaining 1 unit |
| **Expected** | Credit note for remaining 50% of deposit; total = 100% |
| **Result** | |

### TC-DP-014: Over-refund guard — cannot exceed total deposit amount

| Field | Value |
|-------|-------|
| **Precondition** | Full deposit already refunded via credit notes |
| **Steps** | 1. Try to trigger another deposit refund |
| **Expected** | No additional credit note created; system detects over-refund |
| **Result** | |

### TC-DP-015: Auto-refund mode creates payment automatically

| Field | Value |
|-------|-------|
| **Precondition** | `deposit_auto_refund=True`; deposit invoice paid |
| **Steps** | 1. Return all items |
| **Expected** | Credit note created AND payment automatically registered via `account.payment.register` |
| **Result** | |

### TC-DP-016: Manual refund mode — credit note only (no auto payment)

| Field | Value |
|-------|-------|
| **Precondition** | `deposit_auto_refund=False`; deposit invoice paid |
| **Steps** | 1. Return all items |
| **Expected** | Credit note created only; no automatic payment |
| **Result** | |

---

## 5. Deposit Sync Wizard Flow

### TC-DP-017: Confirm with mismatch opens sync wizard

| Field | Value |
|-------|-------|
| **Precondition** | Rental order with unsynced deposit (qty changed but deposits not synced) |
| **Steps** | 1. Click "Confirm" |
| **Expected** | Sync wizard opens with mismatch description |
| **Result** | |

### TC-DP-018: Mismatch info describes what changed

| Field | Value |
|-------|-------|
| **Precondition** | Sync wizard is open |
| **Steps** | 1. Read `mismatch_info` text |
| **Expected** | Bullet points list which lines are out of sync (product name, expected vs actual deposit) |
| **Result** | |

### TC-DP-019: "Sync & Continue" syncs and confirms order

| Field | Value |
|-------|-------|
| **Precondition** | Sync wizard open for "Confirm" action |
| **Steps** | 1. Click "Sync & Continue" |
| **Expected** | Deposits synced; order confirmed; `rental_status = pickup` |
| **Result** | |

### TC-DP-020: "Sync & Go Back" syncs and returns to form

| Field | Value |
|-------|-------|
| **Precondition** | Sync wizard open |
| **Steps** | 1. Click "Sync & Go Back" |
| **Expected** | Deposits synced; wizard closed; user stays on order form |
| **Result** | |

### TC-DP-021: "Continue as Is" skips sync

| Field | Value |
|-------|-------|
| **Precondition** | Sync wizard open |
| **Steps** | 1. Click "Continue as Is" |
| **Expected** | Order confirmed without syncing deposits |
| **Result** | |

---

## 6. Deposit on Invoices

### TC-DP-022: Deposit invoice shows correct amount

| Field | Value |
|-------|-------|
| **Precondition** | Deposit line: 2 units × 5,000 = 10,000 |
| **Steps** | 1. Create invoice<br>2. Open deposit invoice |
| **Expected** | Invoice total = 10,000 THB |
| **Result** | |

### TC-DP-023: Rental invoice does NOT include deposit line

| Field | Value |
|-------|-------|
| **Precondition** | Order with rental lines and deposit line |
| **Steps** | 1. Create invoices<br>2. Open rental invoice (non-deposit) |
| **Expected** | Deposit product not listed in rental invoice lines |
| **Result** | |

### TC-DP-024: Deposit line subtotal shown separately on order

| Field | Value |
|-------|-------|
| **Precondition** | Order with rental + deposit lines |
| **Steps** | 1. Check order form totals |
| **Expected** | `deposit_lines_subtotal` field shows deposit total only |
| **Result** | |

### TC-DP-025: Rental lines subtotal excludes deposit

| Field | Value |
|-------|-------|
| **Precondition** | Order with rental + deposit lines |
| **Steps** | 1. Check `rental_lines_subtotal` field |
| **Expected** | Value = sum of rental lines only (deposit excluded) |
| **Result** | |
