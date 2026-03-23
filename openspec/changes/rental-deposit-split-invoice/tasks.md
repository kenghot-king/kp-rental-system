## 1. Deposit Product Flag

- [x] 1.1 Add `is_rental_deposit` Boolean field to `product.template` in the rental model
- [x] 1.2 Add the field to the product form view (checkbox in the general information section)

## 2. Invoice Split

- [x] 2.1 Override `sale.order._create_invoices()` and `_get_invoiceable_lines()` to split deposit/non-deposit lines
- [x] 2.2 Add helper on `sale.order.line` to determine if line is a deposit line (`_is_rental_deposit_line()`)

## 3. Auto Credit Note on Return

- [x] 3.1 Add method `_create_deposit_credit_note()` on `sale.order.line` that finds the deposit line's posted invoice and creates a proportional credit note
- [x] 3.2 Call `_create_deposit_credit_note()` from `_create_rental_return()` after stock move is done
- [x] 3.3 Handle edge cases: no deposit line, deposit not invoiced, total credits already equal deposit amount

## 4. Verification

- [ ] 4.1 Test: SO with rental + deposit lines creates two separate invoices
- [ ] 4.2 Test: Full return auto-creates credit note for full deposit amount
- [ ] 4.3 Test: Partial return auto-creates proportional credit note
- [ ] 4.4 Test: Return without deposit line creates no credit note
- [ ] 4.5 Test: Return when deposit not yet invoiced creates no credit note
