## 1. Company Field

- [x] 1.1 Add `auto_confirm_invoice = fields.Boolean("Auto Confirm Invoice", default=True)` to `res.company` in `models/res_company.py`

## 2. Settings

- [x] 2.1 Add `auto_confirm_invoice` related field (readonly=False) to `res.config.settings` in `models/res_config_settings.py`
- [x] 2.2 Add "Auto Confirm Invoice" setting under the Pickup block in `views/res_config_settings_views.xml` with help text: "Automatically confirm (post) invoices immediately after creation from a rental order, making them ready for payment."

## 3. Auto-Post Logic

- [x] 3.1 Override `_create_invoices()` in `models/sale_order.py` — after calling `super()`, collect rental-origin invoices by tracing `invoice_line_ids → sale_line_ids → order_id → is_rental_order`
- [x] 3.2 If `company.auto_confirm_invoice` is enabled, call `action_post()` on the rental-origin invoices inside a `try/except` — on exception log a warning with `_logger.warning(...)` and continue (do not raise)
- [x] 3.3 Return the full invoice recordset regardless of post success/failure
