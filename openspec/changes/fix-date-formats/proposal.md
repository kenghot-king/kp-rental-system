## Why

All displayed dates in the rental system use Odoo's locale-dependent "short" format, which renders as M/D/YY (American) when the user language is `en_US`. All dates must display in `dd/MM/yyyy` format and all times in 24-hour `HH:mm` format, consistently across the UI, printed reports, and contracts.

## What Changes

- **`sale_order_line.py` — rental period description**: `_get_rental_order_line_description()` calls `format_datetime` with `dt_format='short'`; change to explicit `'dd/MM/yyyy, HH:mm'`. Same-day return uses `format_time` with `time_format='short'`; change to `'HH:mm'`.
- **Rental order report** (`rental_order_report_templates.xml`): Add `t-options` with explicit datetime format to `line.start_date` and `line.return_date` columns.
- **Thai tax invoice** (`report_invoice_thai.xml`): Add `t-options` with explicit date format to `o.invoice_date` and `o.invoice_date_due`.
- **Rental contract** (`rental_contract_templates.xml`): Add explicit format to `doc.rental_start_date` (header date field) and add `t-options` to the period table fields `doc.rental_start_date` / `doc.rental_return_date`.

## Capabilities

### New Capabilities

- `date-display-format`: All rental system dates render in `dd/MM/yyyy` (date) or `dd/MM/yyyy HH:mm` (datetime) format, independent of the Odoo user's language locale.

### Modified Capabilities

<!-- No existing spec-level requirement changes -->

## Impact

- `addons/ggg_rental/models/sale_order_line.py` — model-layer date formatting
- `addons/ggg_rental/report/rental_order_report_templates.xml` — report template date fields
- `addons/ggg_rental/report/report_invoice_thai.xml` — invoice template date fields
- `addons/ggg_rental/report/rental_contract_templates.xml` — contract template date fields
