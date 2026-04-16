# Tasks: pickup-payment-gate

- [x] 1. Add `require_payment_before_pickup` Boolean field to `res.company` (default `False`, under `# Deposit` or new `# Pickup` section)
- [x] 2. Add related field `require_payment_before_pickup` to `res.config.settings`, expose in `res_config_settings_views.xml` under a new "Pickup" block in the Rental app section
- [x] 3. In `sale.order.action_open_pickup()`: add payment gate check guarded by `self.company_id.require_payment_before_pickup`
