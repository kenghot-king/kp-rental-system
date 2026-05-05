## 1. Quotation total label override

- [x] 1.1 Create `addons/ggg_rental/i18n/th.po` with a valid PO header and a single entry: `msgid "Total"` / `msgstr "ยอดรวม"`
- [ ] 1.2 Upgrade the ggg_rental module so the new translation loads (or run `--i18n-overwrite` on a dev DB)
- [ ] 1.3 Verify quotation PDF renders "ยอดรวม" instead of "ทั้งหมด" in the o_total row when printed in Thai

## 2. Rental contract "รวม" column → VAT-included

- [x] 2.1 In `rental_contract_templates.xml`, change line ~126 from `'{:,.2f}'.format(line.price_subtotal)` to `'{:,.2f}'.format(line.price_total)` for the rental_lines table
- [x] 2.2 Confirm the deposit_lines table remains on `price_subtotal` (deposits are zero-tax)
- [ ] 2.3 Verify rental contract PDF column "รวม" displays the VAT-included amount per item (e.g., 1,590 × qty for a 7% VAT item with unit price 1,486.92)

## 3. Rental contract financial summary — tax group breakdown + reconciling footer

- [x] 3.1 At the top of the financial summary, add a row "ยอดรวมค่าเช่า (รวมภาษี)" computed as `sum(rental_lines.mapped('price_total'))`
- [x] 3.2 Move/keep `เงินประกัน` row in its current position (right after the new incl-VAT row)
- [x] 3.3 Add a row "ยอดรวมค่าเช่า (ไม่รวมภาษี)" using the existing `doc.rental_lines_subtotal`
- [x] 3.4 Replace the single `<tr t-if="doc.amount_tax">…ภาษี…</tr>` block with `<t t-foreach="doc.tax_totals['subtotals']" t-as="subtotal"><t t-foreach="subtotal['tax_groups']" t-as="tax_group">` rendering one row per group with `tax_group['group_name']` and `tax_group['tax_amount_currency']`
- [x] 3.5 Keep the `ยอดรวมทั้งสิ้น` row using `doc.amount_total`
- [ ] 3.6 Verify column-to-footer reconciliation: sum of "รวม" column = "ยอดรวมค่าเช่า (รวมภาษี)"
- [ ] 3.7 Verify breakdown reconciliation: "ยอดรวมค่าเช่า (ไม่รวมภาษี)" + Σ(tax group rows) + "เงินประกัน" = "ยอดรวมทั้งสิ้น"
- [ ] 3.8 Verify a contract with no taxed lines hides all tax group rows (no empty rows render)
- [ ] 3.9 Verify a contract with two or more distinct tax groups renders one row per group, each labeled with its `group_name`

## 4. Manual validation

- [ ] 4.1 Print quotation PDF and confirm "ยอดรวม" label appears in o_total row
- [ ] 4.2 Print rental contract PDF and confirm: รวม column is incl-VAT, financial summary shows both subtotals plus per-tax-group rows, and totals reconcile
- [ ] 4.3 Print a rental contract that has no VAT (e.g., zero-tax product) and confirm tax group rows are absent
