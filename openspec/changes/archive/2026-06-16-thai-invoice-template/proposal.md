## Why

Customers require printed invoices in a Thai-standard format (bilingual Thai/English) with VAT/NON-VAT separation, withholding tax display, amount in Thai words, and signature blocks — none of which the default Odoo invoice template provides. The current template does not meet Thai tax invoice documentation requirements for B2B transactions.

## What Changes

- Replace the default Odoo invoice PDF output with a fully custom Thai-format template for all `out_invoice` documents
- New QWeb template renders: company header, bilingual title (ต้นฉบับ ใบแจ้งหนี้ / INVOICE ORIGINAL), customer/invoice info block, line items table with VAT CODE column, VAT vs NON-VAT subtotal split, withholding tax deduction, amount in Thai words, cheque payment note, and dual signature blocks
- Override `account.move._get_name_invoice_report()` so the wrapper selects our template
- Add `amount_in_thai_words` computed field/method on `account.move` using `num2words(lang='th', to='currency')`
- No new UI views or menu items; purely a print output change

## Capabilities

### New Capabilities

- `thai-invoice-pdf`: Full-page Thai-format invoice PDF replacing the standard Odoo invoice template, including bilingual labels, VAT/NON-VAT line grouping, withholding tax detection, Thai baht amount in words, and signature blocks

### Modified Capabilities

<!-- No existing specs change requirements -->

## Impact

- **`addons/ggg_rental/report/`** — new `report_invoice_thai.xml` (QWeb template + report_invoice override)
- **`addons/ggg_rental/models/account_move.py`** — new method `amount_in_thai_words()`, override `_get_name_invoice_report()`
- **`addons/ggg_rental/__manifest__.py`** — register new XML
- **`l10n_th`** — depends on it for `l10n_th_branch_name` field on `res.partner`; our override co-exists with l10n_th's elif pattern
- **`num2words`** — already installed in the container (verified); `lang='th'`, `to='currency'` produces correct Thai baht text
- All printed invoices (out_invoice) will use the new layout — no opt-out per document
