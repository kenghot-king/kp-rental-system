## Context

Phase 1 payments are manual — staff process charges via external 2c2p (online) and EDC (in-store) terminals, then record payments in Odoo. Currently there's no way to store the external transaction reference on the Odoo payment record, making reconciliation difficult.

`account.payment` already has a `payment_reference` Char field (for check numbers, file names, etc.) but it's not shown in the form view. We reuse this as Reference 1 and add a second field.

## Goals / Non-Goals

**Goals:**
- Staff can enter two external references (2c2p ref, EDC ref, etc.) when registering a rental payment
- References are only visible on rental-related payments (not cluttering non-rental workflows)
- References are stored permanently on `account.payment` for accounting reconciliation

**Non-Goals:**
- No 2c2p or EDC system integration (Phase 2+)
- No validation of reference format
- No auto-copy of refs to refund payments

## Decisions

### 1. Rental detection via computed `is_rental_payment` (Option 3)

Computed stored boolean on `account.payment` that traces: payment → reconciled move lines → invoice move → sale order lines → `is_rental_order`.

**Why not XML-only traversal (Option 1)?** Odoo XML `invisible` conditions cannot traverse the multi-hop m2m path from payment to sale order. A computed field keeps the view logic clean (`invisible="not is_rental_payment"`).

**Compute trigger:** Depends on `reconciled_invoice_ids` — recomputes when payment is matched to invoices.

### 2. Reuse `payment_reference` as Reference 1

The field already exists, is tracked, and has the right semantics. No migration needed — just show it in the view.

### 3. Register wizard pass-through

Add both fields to `account.payment.register` wizard. On payment creation, pass values through to the `account.payment` record. This lets staff enter refs at payment time instead of editing afterward.

## Risks / Trade-offs

- **[Risk] `is_rental_payment` may be False at payment registration time** — if payment isn't yet reconciled with an invoice, `reconciled_invoice_ids` is empty. → Mitigation: Also check `reconciled_bill_ids` and consider using the context or the source move to detect rental origin. Alternatively, compute from the move's `line_ids.sale_line_ids`.
- **[Risk] Register wizard creates payment without refs** — if staff skips the fields in the wizard, they must edit the payment afterward. → Acceptable: fields are optional, same as current `memo` behavior.
