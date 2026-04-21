# Design: pickup-payment-gate

## Setting: `require_payment_before_pickup`

Stored on `res.company` as a Boolean, default `False`.
Surfaced in `res.config.settings` as a related field (same pattern as `deposit_auto_refund`).
Shown in Rental Settings under a new "Pickup" block.

## Check Logic

Inserted at the top of `sale.order.action_open_pickup()`, before the line filter:

```python
if self.company_id.require_payment_before_pickup:
    posted_invoices = self.invoice_ids.filtered(
        lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
    )
    if not posted_invoices:
        raise UserError(_("Cannot process pickup: no invoice has been issued for this order."))
    unpaid = posted_invoices.filtered(lambda inv: inv.payment_state != 'paid')
    if unpaid:
        raise UserError(_(
            "Cannot process pickup: the following invoice(s) are not fully paid: %s",
            ', '.join(unpaid.mapped('name'))
        ))
```

## Decisions

### Which invoices are checked?
All posted customer invoices (`state='posted'`, `move_type='out_invoice'`).
- Credit notes (`out_refund`) are excluded — they are not customer obligations.
- Draft invoices are excluded — not yet confirmed obligations.

### What counts as "paid"?
`payment_state == 'paid'` only.  
`in_payment` and `partial` are not accepted — consistent with the user's stated requirement.

### Default value
`False` — the gate is off by default so existing deployments are unaffected.

### Split-invoice scenario
With the `rental-deposit-split-invoice` change active, a typical order has:
1. Deposit invoice — posted and paid before pickup
2. Rental fee invoice — may be posted before or after pickup

When the setting is enabled, **both** must be fully paid before pickup is allowed.  
If the workflow intends the rental fee invoice to be issued after return, staff should not post the rental invoice until after pickup. This is a workflow concern, not a code concern.

### No UI indicator on the SO form
The button invisibility condition is not changed. The block is only surfaced as a `UserError` when the button is clicked. Adding a computed warning field is out of scope.
