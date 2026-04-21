## Why

The rental business accepts payments through many real-world channels — cash, multiple EDC terminals across card brands (VISA/Master/JCB/AMEX/UnionPay), Thai QR to different destination banks, and online gateways. Today every payment looks the same in `account.payment`: a journal and a generic "Manual Payment" method. Staff cannot slice daily income by channel, attribute collections to the cashier who took them, or record the approval code needed for EDC dispute handling. This change lays the data foundation — categorization, attribution, and audit metadata — that a follow-on change (`daily-payment-reconciliation`) will use to produce the end-of-day cashier report.

## What Changes

- Add `channel_type` selection on `account.journal` (`cash`, `edc`, `qr`, `online`, `other`) — admin configured per journal, used purely for reporting classification (no UI visibility logic)
- Add `cashier_id` Many2one field on `account.payment` — defaults to `env.user` via the register wizard, identifies who collected the payment
- Add `approval_code` Char field on `account.payment` — always visible, not required, captures EDC approval code / QR transaction ID / online gateway ref
- Add `display_method` computed Char on `account.payment` — reads `payment_method_line_id.name`, used as the grouping/reporting key
- Extend `account.payment.register` wizard to expose `approval_code` and auto-populate `cashier_id`, passing both through to the created payment (mirrors the existing `rental-payment-refs` pattern)
- **No** custom `card_brand` field — card brands and gateway variants are modeled as `account.payment.method.line` entries per journal (native Odoo mechanism, admin-configured, wraps the standard "Manual Payment" method)

## Capabilities

### New Capabilities
- `payment-channel-metadata`: Cashier attribution, channel classification on journals, approval code capture, and display-method computation on `account.payment`

### Modified Capabilities
<!-- None — the rental-payment-refs capability remains untouched; this change adds new fields without modifying existing payment-reference requirements -->

## Impact

- `account.journal` model — new `channel_type` selection field; admins must categorize each rental-facing journal
- `account.journal` form view — inherited view to show `channel_type`
- `account.payment` model — new `cashier_id`, `approval_code`, `display_method` fields
- `account.payment` form view — inherited view to show the new fields
- `account.payment.register` wizard — new fields on the wizard + pass-through logic
- `ggg_rental` module — continues to extend `account` module (existing dependency)
- Data setup (operational, not module): admin must configure `inbound_payment_method_line_ids` per journal with display names matching card brands / gateway sub-methods
