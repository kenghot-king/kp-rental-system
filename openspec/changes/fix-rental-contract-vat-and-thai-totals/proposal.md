## Why

Two related rental document display issues for the Thai-only deployment:

1. **Quotation/sale order PDF displays "ทั้งหมด"** as the total label (Odoo's default Thai translation of "Total"). Business prefers "ยอดรวม", the more formal financial term already used by the hardcoded headers on the rental contract (`ยอดรวมค่าเช่า`, `ยอดรวมเงินประกัน`, `ยอดรวมทั้งสิ้น`).

2. **Rental contract PDF (`สัญญาเช่า`)** shows the per-line "รวม" column as the ex-VAT subtotal, which is misleading for a customer-facing document where the gross/VAT-included amount is the relevant figure. The contract also collapses tax into a single bare "ภาษี" row, hiding which tax group(s) and rate(s) apply, in contrast to the quotation which already itemizes by tax group.

## What Changes

- Add `addons/ggg_rental/i18n/th.po` re-translating `msgid "Total"` → `msgstr "ยอดรวม"` for any string rendered through the rental module's reports.
- In `rental_contract_templates.xml`, change the rental items "รวม" column data source from `line.price_subtotal` to `line.price_total` (VAT-included). Deposit table is unchanged (deposits are zero-tax in TH).
- Replace the single bare "ภาษี" row in the contract financial summary with one row per tax group, sourced from `doc.tax_totals['subtotals'][*]['tax_groups'][*]`, displaying each `group_name` (e.g., "ภาษีมูลค่าเพิ่ม 7%") and `tax_amount_currency`.
- Restructure the contract financial summary so the รวม column reconciles to the footer: add a "ยอดรวมค่าเช่า (รวมภาษี)" line equal to the sum of incl-VAT line totals; rename the existing ex-VAT row to "ยอดรวมค่าเช่า (ไม่รวมภาษี)"; keep the per-tax-group rows for accounting transparency; preserve `เงินประกัน` and `ยอดรวมทั้งสิ้น` unchanged.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `rental-document-templates`: quotation total label translation, rental contract per-line column semantics, and rental contract financial summary structure are all changing.

## Impact

- `addons/ggg_rental/i18n/th.po` — new file (Odoo auto-discovers `i18n/*.po`; no manifest edit required)
- `addons/ggg_rental/report/rental_contract_templates.xml` — column source change at the rental items table; financial summary restructured with per-tax-group loop
