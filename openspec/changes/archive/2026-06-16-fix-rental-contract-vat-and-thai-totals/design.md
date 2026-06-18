## Context

Three rendering decisions interact in this change:

**1. Quotation total label translation.** The base `account.document_tax_totals_template` renders `<strong>Total</strong>`, translated via Odoo's `account` module th.po to `ทั้งหมด`. Business prefers `ยอดรวม`, which is consistent with the rental contract's hardcoded Thai headers. Since the deployment is Thai-only, an Odoo module-level i18n override (`ggg_rental/i18n/th.po`) re-translates the same `msgid` and takes precedence when ggg_rental is loaded.

**2. Rental contract "รวม" column semantics.** Today the column displays `line.price_subtotal` (ex-VAT). The customer-facing intent of "รวม" is the gross amount payable per item, not the accounting subtotal. Switching to `line.price_total` (incl-VAT) matches that intent. Deposit lines are zero-tax in Thai practice so `price_subtotal == price_total` for the deposit table — no visual change there.

**3. Tax breakdown in financial summary.** The contract currently shows a single `ภาษี` row with `doc.amount_tax`. The quotation, by contrast, iterates `tax_totals['subtotals'][*]['tax_groups']` and renders one row per group with its `group_name` (e.g., `ภาษีมูลค่าเพิ่ม 7%`). `doc.tax_totals` is already populated by Odoo on `sale.order`, so the contract template can iterate the same dict without any model change.

Because the per-line column is changing to incl-VAT (decision 2) but the tax breakdown stays visible (decision 3), the footer must reconcile both views — the column sum must equal an incl-VAT subtotal line in the footer, and the ex-VAT subtotal + per-tax-group rows + deposit must independently sum to the grand total.

## Goals / Non-Goals

**Goals:**
- Quotation PDF displays `ยอดรวม` instead of `ทั้งหมด` for the total label.
- Rental contract `รวม` column displays VAT-included per-line amounts.
- Rental contract financial summary itemizes tax by tax group, matching the quotation's data source.
- Rental contract financial summary visibly reconciles: column sum equals an incl-VAT subtotal row; ex-VAT subtotal + tax rows + deposit equals the grand total.

**Non-Goals:**
- Changing how Odoo computes `price_total` or `tax_totals`.
- Changing the deposit table (deposits remain ex-VAT == incl-VAT in Thai accounting practice).
- Changing the quotation's per-tax-group row layout (already correct).
- Changing the standalone Thai invoice template (`report_invoice_thai.xml`) — its bilingual labels are out of scope.
- Re-labeling "ภาษี" to a generic Thai term (e.g., `ภาษีถัวเฉลี่ย`). Business has not confirmed wording, and Option A (per-tax-group names) sidesteps the question by labeling each row with the actual `tax_group_id.name`.

## Decisions

### i18n override scope

Place the override in `addons/ggg_rental/i18n/th.po` rather than editing the contract template or adding XPath swaps. Reasons:

- The source `msgid "Total"` lives in base Odoo (`account` module). A module-level th.po that re-translates the same msgid takes precedence when ggg_rental is loaded.
- It degrades gracefully if Odoo ever changes the source string — the override silently no-ops rather than producing a broken XPath.
- It keeps the rendered text consistent across any future report inheriting `sale.document_tax_totals` from this module.

**Alternative considered — XPath swap of `<strong>Total</strong>`:** rejected because it bakes a Thai literal into the template, breaks if anyone prints in another language, and bypasses the existing translation pipeline.

### Footer layout (Option Z — both views)

The financial summary will read:

```
ยอดรวมค่าเช่า (รวมภาษี)              <Σ rental_lines.price_total>
เงินประกัน                          <doc.deposit_lines_subtotal>
ยอดรวมค่าเช่า (ไม่รวมภาษี)            <doc.rental_lines_subtotal>
<for each tax_group in doc.tax_totals>
  <tax_group.group_name>            <tax_group.tax_amount_currency>
ยอดรวมทั้งสิ้น                       <doc.amount_total>
```

The first row reconciles to the รวม column. The ex-VAT subtotal + tax group rows + เงินประกัน sum to the grand total, preserving the existing breakdown for accounting transparency. Row count grows by 1 + N(tax_groups) compared to today, in exchange for both per-line and aggregate clarity.

**Alternative Y (drop ภาษี from footer entirely):** rejected — Thai rental contracts are commonly used as supporting documentation for VAT-claimable expenses; the breakdown should remain visible.

**Alternative X (column ≠ footer subtotal):** rejected — the visual mismatch invites customer questions and trust issues.

### Tax data source

Use `doc.tax_totals['subtotals'][*]['tax_groups']` rather than computing from `rental_lines.tax_ids` directly. Reasons:

- Zero new code paths; Odoo already computes this on `sale.order` via `_get_tax_totals`.
- Identical data shape to the quotation, ensuring rendering parity.

**Caveat:** this includes any taxed deposit lines in the breakdown. Thai deposits are conventionally zero-tax, so in practice the sum equals rental tax. If a future deposit line is taxed, the contract footer remains correct — the line just appears under its tax group with the deposit's tax included. Acceptable.

## Risks / Trade-offs

- **i18n override** — If Odoo upgrades and changes the source string from "Total" to e.g. "Grand Total", the override silently stops applying and the label reverts to base translation. Detection: visual QA of quotation PDF after upgrades. Mitigation: low — regression is a label revert, not a math error.
- **Column = price_total** — If a rental product is configured with a price-included tax (i.e., `price_unit` already includes VAT), `price_total` is still correct because Odoo handles tax-included pricing inside `_compute_amount`. No special case needed.
- **tax_totals row growth** — A contract with N distinct tax groups grows the financial summary by N rows. The summary block already has `page-break-inside: avoid` (line 177); if it overflows the page, normal pagination kicks in. Acceptable.
- **Pending Business decision on label wording** — Business has not confirmed whether they want a different generic label. Option A obviates the question by using each group's actual name. If Business later wants a single rolled-up label, that would be a follow-up change — not blocking.
