## Why

Phase 1 payment processing is manual (no 2c2p/EDC system integration). Staff need reference fields on payment records to cross-reference external payment transactions (2c2p, EDC) for reconciliation with accounting.

## What Changes

- Show existing `payment_reference` field (Reference 1) on `account.payment` form — visible only for rental-related payments
- Add new `payment_reference_2` Char field (Reference 2) on `account.payment` — visible only for rental-related payments
- Add computed `is_rental_payment` boolean on `account.payment` to determine rental context (traces payment → invoice → sale order → `is_rental_order`)
- Optionally surface both fields on `account.payment.register` wizard so staff can enter refs at payment time

## Capabilities

### New Capabilities
- `rental-payment-refs`: Reference fields on payment records for tracking external payment transaction IDs (2c2p, EDC) in rental context

### Modified Capabilities
<!-- None — no existing specs are changing -->

## Impact

- `account.payment` model — new field + computed field
- `account.payment` form view — inherited view to show fields conditionally
- `account.payment.register` wizard — optional: fields + pass-through to payment
- `ggg_rental` module — new dependency awareness of `account` module (already implicit)
