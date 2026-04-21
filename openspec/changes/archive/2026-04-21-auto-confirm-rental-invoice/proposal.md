## Why

When `Require Payment Before Pickup` is enabled, invoices must be posted before the payment gate can check them — but invoices created from rental orders are always created as drafts, forcing staff to manually confirm each one before registering payment. This extra step is unnecessary friction and caused real blocking errors (e.g. S00254) where the pickup gate raised "no invoice has been issued" even though a draft invoice existed.

## What Changes

- Add `auto_confirm_invoice` Boolean field to `res.company` (default `True`)
- Add `auto_confirm_invoice` related field to `res.config.settings`
- Add "Auto Confirm Invoice" setting under the Pickup block in Rental Settings UI, with description: *"Automatically confirm (post) invoices immediately after creation from a rental order, making them ready for payment."*
- Override `_create_invoices()` on `sale.order` to auto-post newly created invoices when the setting is enabled — scoped to rental orders only (`is_rental_order = True`) by tracing invoice lines back to their source order

## Capabilities

### New Capabilities

- `auto-confirm-rental-invoice`: Company-level setting that auto-posts invoices (both rental and deposit) created from rental orders immediately after `_create_invoices()` returns

### Modified Capabilities

## Impact

- `models/res_company.py` — new field
- `models/res_config_settings.py` — new related field
- `views/res_config_settings_views.xml` — new setting under Pickup block
- `models/sale_order.py` — `_create_invoices()` override with scoped auto-post logic
