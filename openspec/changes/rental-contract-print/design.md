# Design: rental-contract-print

## Contract Reference

Use `doc.name` (sale order name, e.g. `S00042`) as the contract reference for now.
No separate sequence — field is left as a future extension point.

## Print Gate Logic

`action_print_rental_contract()` raises `UserError` if:

```
doc.rental_status not in ('pickup', 'return', 'returned')
```

Meaning: the order must be confirmed and at least in "Reserved" state.
Draft, Sent, and Cancelled orders cannot print a contract.

## Template Structure

```
┌──────────────────────────────────────────────────────┐
│  [web.external_layout header — company logo, name]   │
│                                                      │
│  RENTAL AGREEMENT                  S00042            │
│  Date: 16 Apr 2026                                   │
├──────────────────────┬───────────────────────────────┤
│  LESSOR              │  LESSEE                       │
│  Company name        │  partner_id (contact widget)  │
│  Company address     │  Billing address              │
│  Phone / Email       │  Phone                        │
├──────────────────────┴───────────────────────────────┤
│  RENTAL PERIOD                                       │
│  Pickup Date       Return Date       Duration        │
│  20 Apr 09:00      25 Apr 18:00      5 days          │
├──────────────────────────────────────────────────────┤
│  RENTED ITEMS                                        │
│  Product           Qty   Unit Price   Subtotal       │
│  Camera Canon        2     500.00    1,000.00        │
│  Tripod Heavy        1      50.00       50.00        │
│                           Rental Subtotal: 1,050.00  │
├──────────────────────────────────────────────────────┤
│  DEPOSITS  (shown only if deposit lines exist)       │
│  Item               Qty   Unit Price   Amount        │
│  [Deposit] Camera     2     200.00      400.00       │
│  [Deposit] Tripod     1      30.00       30.00       │
│                           Deposit Total:   430.00    │
├──────────────────────────────────────────────────────┤
│  FINANCIAL SUMMARY                                   │
│  Rental Subtotal:                        1,050.00    │
│  Deposit:                                  430.00    │
│  Tax:                                      105.00    │
│  ─────────────────────────────────────────────────   │
│  Grand Total:                            1,585.00    │
├──────────────────────────────────────────────────────┤
│  TERMS & CONDITIONS  (company.rental_contract_terms) │
│  [rich-text, rendered as HTML]                       │
│  Falls back to a standard placeholder if empty.      │
├──────────────────────────────────────────────────────┤
│  ACKNOWLEDGEMENT                                     │
│  I, the undersigned, acknowledge receipt of the      │
│  above items and agree to the terms above.           │
│                                                      │
│  Customer: ___________________  Date: ____________   │
│                                                      │
│  Authorised Staff: ____________ Date: ____________   │
│                                                      │
│  [web.external_layout footer]                        │
└──────────────────────────────────────────────────────┘
```

## Line Filtering

- **Rental lines**: `line.is_rental and not line.deposit_parent_id`
- **Deposit lines**: `line.deposit_parent_id`
- All other lines (service fees, notes, etc.) are excluded from the contract

Deposit section is wrapped in `t-if` and only rendered if at least one deposit line exists.

## Terms Field

`res.company.rental_contract_terms` — `fields.Html`, company-dependent.
Rendered in the template via `t-out="doc.company_id.rental_contract_terms"`.

Fallback placeholder (shown when field is empty):
> *The renter is responsible for all damage, loss, or theft of the rented items during the rental period.
> Items must be returned by the agreed return date and time. Late returns will incur additional charges.*

## Button Placement

The "Print Contract" button sits in the sale order form's top button bar,
visible only when `is_rental_order = True`.
It calls `action_print_rental_contract` directly (no wizard).

## Currency / Tax Display

Use `doc.currency_id` for all monetary values.
Tax totals drawn from `doc.amount_tax` (standard SO field).
Grand Total = `doc.amount_total`.

Rental subtotal = sum of `price_subtotal` for rental lines.
Deposit total = sum of `price_subtotal` for deposit lines.
