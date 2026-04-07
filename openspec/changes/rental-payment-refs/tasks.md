## 1. Payment Model Extension

- [x] 1.1 Add `payment_reference_2` Char field to `account.payment`
- [x] 1.2 Add computed stored `is_rental_payment` boolean to `account.payment` (traces reconciled invoices → sale order → `is_rental_order`)
- [x] 1.3 Register `account.payment` model extension in `models/__init__.py`

## 2. Payment Form View

- [x] 2.1 Inherit `account.payment` form view to show `payment_reference` (Reference 1) and `payment_reference_2` (Reference 2), both with `invisible="not is_rental_payment"`

## 3. Payment Register Wizard

- [x] 3.1 Add `payment_reference` and `payment_reference_2` fields to `account.payment.register`
- [x] 3.2 Override `_create_payment_vals_from_wizard` (or equivalent) to pass reference fields through to the created `account.payment`
- [x] 3.3 Inherit register wizard form view to show both fields conditionally (when source invoice is from a rental order)

## 4. Module Registration

- [x] 4.1 Add new view XML files to `__manifest__.py`
