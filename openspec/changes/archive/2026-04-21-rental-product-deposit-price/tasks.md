## 1. Product Model

- [x] 1.1 Add `deposit_price` field (`Float`, `company_dependent=True`, string="Deposit Price") to `product.template` in `addons/ggg_rental/models/product_template.py`

## 2. Product Form View

- [x] 2.1 Add `deposit_price` field to the rental tab in the product form view (after existing rental pricing fields)

## 3. Deposit Sync Logic

- [x] 3.1 In `action_sync_deposits()` (`sale_order.py`): change `expected_price` from `line.product_id.list_price` to `line.product_id.deposit_price`
- [x] 3.2 In `action_sync_deposits()`: change tax source from `line.tax_ids` to `deposit_product.taxes_id` — update both the create and update branches
- [x] 3.3 In `_check_deposit_sync()`: remove the price mismatch check (`deposit.price_unit != line.product_id.list_price`)
