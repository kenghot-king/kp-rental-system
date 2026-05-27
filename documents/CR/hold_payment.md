# Hold Payment — Deposit Invoice Flow

## Overview

When a customer pays a security deposit via credit card hold (pre-authorization), the system
creates a hold payment in `processing` state instead of posting a real payment. The deposit
invoice remains outstanding until the hold is either forfeited (No Show) or released (customer returns).

## Journals

| Journal | `for_hold` | Allowed on Rental Invoice | Allowed on Deposit Invoice |
|---------|-----------|--------------------------|---------------------------|
| EDC     | False      | Yes                      | Yes → paid immediately     |
| HLD     | True       | No (blocked)             | Yes → hold state           |

## Document Types

| Scenario | Document Printed |
|----------|-----------------|
| Deposit paid via EDC (money received) | ใบเสร็จ (Receipt) |
| Deposit paid via HLD (credit hold)    | ใบมัดจำ (Deposit Certificate) |
| Deposit forfeited (No Show)           | ใบเสร็จ (Receipt) stamped with forfeiture date |

---

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Staff
    participant SO as Sale Order
    participant RInv as Rental Invoice
    participant DInv as Deposit Invoice
    participant HPay as Hold Payment

    %% SO CONFIRM
    Staff->>SO: Confirm Order
    SO->>RInv: Create and Auto-post Rental Invoice
    SO->>DInv: Create and Auto-post Deposit Invoice
    Note over RInv,DInv: Two invoices, state=posted, payment_state=not_paid

    %% RENTAL INVOICE
    Note over Staff,RInv: Flow 1 - Rental Invoice Normal Payment
    Staff->>RInv: Register Payment (EDC)
    RInv->>RInv: payment_state = paid
    Staff->>RInv: Print Receipt

    %% DEPOSIT EDC PATH
    Note over Staff,DInv: Flow 2 - Deposit paid via EDC (money received)
    Staff->>DInv: Register Payment (EDC, for_hold=false)
    DInv->>DInv: payment_state = paid
    Staff->>DInv: Print Receipt

    %% DEPOSIT HLD PATH
    Note over Staff,HPay: Flow 3 - Deposit paid via HLD (credit hold)
    Staff->>DInv: Register Payment (HLD, for_hold=true)
    DInv->>HPay: Create account.payment, is_deposit_hold=True, state=processing
    Note over HPay: NOT posted, no journal entry, approval_code and ref_2 stored
    DInv->>DInv: deposit_hold_state = hold
    DInv->>DInv: Show badge On Hold, show buttons Unhold and Forfeit
    Staff->>DInv: Print Deposit Certificate

    %% GUARD: HLD on Rental Invoice
    Note over Staff,RInv: Guard - HLD journal blocked on Rental Invoice
    Staff-->>RInv: Try Register Payment (HLD)
    RInv-->>Staff: Error - Hold journal not allowed on rental invoice

    %% FORFEIT PATH
    Note over Staff,DInv: Flow 4 - Forfeit, Customer does not show up
    Staff->>DInv: Click Forfeit
    DInv->>Staff: Wizard - enter forfeiture date, default today
    Staff->>DInv: Confirm forfeiture date
    DInv->>HPay: Update payment date to forfeiture date
    DInv->>HPay: action_post(), state = posted
    HPay->>DInv: Reconcile with invoice
    DInv->>DInv: payment_state = paid, deposit_hold_state = none
    Staff->>DInv: Print Receipt stamped with forfeiture date

    %% UNHOLD + RETURN PATH
    Note over Staff,DInv: Flow 5 - Unhold, Customer returns equipment
    Staff->>DInv: Click Unhold
    DInv->>HPay: state = draft
    Note over HPay: Hold released, pre-auth cancelled
    DInv->>DInv: deposit_hold_state = none, payment_state = not_paid
    Staff->>SO: Process Return, qty_returned updated
    SO->>DInv: _create_deposit_credit_note()
    Note over DInv: Guard skips CN if deposit_hold_state = hold, safe here as hold released
    DInv->>DInv: Credit Note created and posted
    DInv->>DInv: CN reconciled, payment_state = paid
    DInv->>HPay: Cancel hold payment (state = cancel, record kept for audit/report)
```

---

## Payment State Transitions

```mermaid
graph LR
    A((Start)) --> B[draft]
    B -->|Hold confirmed| C[processing]
    C -->|Unhold| B
    C -->|Forfeit| D[posted]
    B -->|CN reconciled| F[cancelled]
    F --> E((End))
    D -->|Invoice paid| E
```

---

## Key Fields

| Model | Field | Purpose |
|-------|-------|---------|
| `account.journal` | `for_hold` (Boolean) | Marks journal as credit hold type |
| `account.payment` | `is_deposit_hold` (Boolean) | Marks payment as a hold (not a real receipt) |
| `account.payment` | `state = 'processing'` | Custom state: hold active, not yet posted |
| `account.payment` | `state = 'cancel'` | Hold released and CN reconciled — record kept for reporting (approval_code, ref_2 preserved) |
| `account.move` | `deposit_hold_state` (Computed) | `'none'` or `'hold'` — drives UI buttons and badge |

## Guards

| Guard | Location | Condition |
|-------|----------|-----------|
| Block HLD on rental invoice | `account.move.action_register_payment` | `journal.for_hold=True` and invoice is not deposit |
| Block normal post of processing payment | `account.payment.action_post` | `is_deposit_hold=True` and not called from forfeit flow |
| Skip CN creation during active hold | `sale_order_line._create_deposit_credit_note` | `deposit_invoice.deposit_hold_state == 'hold'` |
