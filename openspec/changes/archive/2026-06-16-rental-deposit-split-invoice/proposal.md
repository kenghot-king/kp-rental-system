## Why

Rental orders often include a security deposit line alongside the rental item lines. Currently, all lines are invoiced together in a single invoice, making it difficult to refund the deposit separately when equipment is returned. Splitting deposit and rental lines into separate invoices enables independent lifecycle management — the rental invoice follows normal payment flow while the deposit invoice can be credited (fully or partially) upon return.

## What Changes

- Add `is_rental_deposit` boolean flag on `product.template` to designate deposit products
- Override `sale.order._get_invoice_grouping_keys()` to split deposit vs non-deposit lines into separate invoices
- Auto-create a proportional credit note when rental items are returned (partial or full return)
- Credit notes are auto-posted (not draft)
- Credit ratio: `returned_qty / delivered_qty × deposit_amount`

## Capabilities

### New Capabilities
- `deposit-product`: Flag products as rental deposit items via a boolean on the product form
- `deposit-invoice-split`: Separate deposit lines from rental lines into distinct invoices during invoicing
- `deposit-auto-refund`: Automatically generate and post a proportional credit note on each return event

### Modified Capabilities

## Impact

- **Models**: `product.template` (new field), `sale.order` (override grouping keys), `sale.order.line` (credit note logic in return flow)
- **Views**: Product form (new checkbox), possibly sale order form (deposit indicator)
- **Dependencies**: Relies on existing `ggg_rental` return flow (`_create_rental_return`)
- **No new module** — extends `ggg_rental`
