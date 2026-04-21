## 1. Fix `_get_invoiceable_lines()`

- [x] 1.1 In `_get_invoiceable_lines()` in `models/sale_order.py`, add a helper check that returns `True` if a deposit line already has a posted `out_invoice` on its `invoice_lines`
- [x] 1.2 Apply that check inside the `_rental_deposit_only` branch: filter out deposit lines where `already_invoiced` is `True`
- [x] 1.3 Apply the same check in the default return (no context flag) so the base `super()._create_invoices()` path is also protected

## 2. Fix the `needs_split` check

- [x] 2.1 In `_create_invoices()`, update the `has_deposit` detection inside the `needs_split` loop to skip deposit lines that already have a posted invoice (mirrors the `_get_invoiceable_lines()` guard)
