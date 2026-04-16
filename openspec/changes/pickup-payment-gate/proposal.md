## Why

There is no payment enforcement before the pickup step. Staff can process a pickup even when the customer has outstanding unpaid invoices. A company setting is needed to optionally enforce that all posted customer invoices on the order are fully paid before pickup is allowed.

## What Changes

- Add `require_payment_before_pickup` Boolean field on `res.company` (default `False`)
- Expose the field in Rental Settings via `res.config.settings`
- In `action_open_pickup()` on `sale.order`: when the company flag is `True`, block with `UserError` if no posted invoices exist or any posted invoice is not fully paid (`payment_state != 'paid'`)

## Capabilities

### New Capabilities
- `pickup-payment-gate`: Company-level setting to require all posted customer invoices to be fully paid before the pickup wizard can be opened on a rental order.

### Modified Capabilities

## Impact

- **Models**: `res.company` (new field), `res.config.settings` (new related field), `sale.order` (`action_open_pickup`)
- **Views**: Rental Settings form (new toggle in Pickup section)
- **Behavior**: Hard block (`UserError`) — no soft warning. Default is off, so existing deployments are unaffected until enabled.
