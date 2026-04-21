## 1. Company Configuration

- [x] 1.1 Add `rental_deposit_product_id` Many2one field to `res.company` with domain `[('is_rental_deposit', '=', True)]`
- [x] 1.2 Add `rental_deposit_product_id` related field to `res.config.settings`
- [x] 1.3 Add the field to the settings form view XML under the Deposit section

## 2. Sale Order Line — Deposit Link Field

- [x] 2.1 Add `deposit_parent_id` Many2one field on `sale.order.line` (→ `sale.order.line`, `ondelete='cascade'`)

## 3. Auto-Create Deposit Line

- [x] 3.1 Override `create()` on `sale.order.line` to auto-create deposit line when a rental product is added
- [x] 3.2 Handle product change via `write()` or `@api.onchange('product_id')` — if product changes to a rental product, create deposit; if changed away, remove old deposit
- [x] 3.3 Raise `UserError` if `company.rental_deposit_product_id` is not set when creating a rental line

## 4. Quantity Sync

- [x] 4.1 Override `product_uom_qty` compute/write on deposit lines to follow `deposit_parent_id.product_uom_qty`

## 5. Auto-Delete

- [x] 5.1 Verify cascade delete works when parent rental line is removed (should be handled by `ondelete='cascade'` on `deposit_parent_id`)

## 6. Read-Only UI

- [x] 6.1 Add `readonly` attribute to deposit line fields (`product_id`, `product_uom_qty`, `price_unit`, `name`) in the SO form view XML, conditioned on `deposit_parent_id` being set

## 7. Integration Verification

- [x] 7.1 Verify deposit lines are picked up by existing invoice split logic (`_create_invoices`, `_get_invoiceable_lines`)
- [x] 7.2 Verify deposit credit note logic (`_create_deposit_credit_note`) works with auto-created deposit lines
