## 1. Model — Rental Order Line Description

- [x] 1.1 In `addons/ggg_rental/models/sale_order_line.py` line 279, change `format_time(env, return_date, tz=tz, time_format='short')` to `format_time(env, return_date, tz=tz, time_format='HH:mm')` (same-day return, time only)
- [x] 1.2 In line 281, change `format_datetime(env, return_date, tz=tz, dt_format='short')` to `format_datetime(env, return_date, tz=tz, dt_format='dd/MM/yyyy, HH:mm')` (multi-day return)
- [x] 1.3 In line 282, change `format_datetime(env, start_date, tz=tz, dt_format='short')` to `format_datetime(env, start_date, tz=tz, dt_format='dd/MM/yyyy, HH:mm')` (start date)
- [x] 1.4 Confirm: create a new rental order or change its dates and verify the line description shows `30/04/2026, 09:00 to 01/05/2026, 23:59` format in the UI

## 2. Rental Order Report Template

- [x] 2.1 In `addons/ggg_rental/report/rental_order_report_templates.xml` line 53, add `t-options='{"widget": "datetime", "format": "dd/MM/yyyy HH:mm"}'` to `<span t-field="line.start_date">`
- [x] 2.2 In line 54, add `t-options='{"widget": "datetime", "format": "dd/MM/yyyy HH:mm"}'` to `<span t-field="line.return_date">`
- [x] 2.3 Confirm: print a rental order PDF and verify Pickup Date and Expected Return columns show `dd/MM/yyyy HH:mm` format

## 3. Thai Tax Invoice Template

- [x] 3.1 In `addons/ggg_rental/report/report_invoice_thai.xml` line 97, add `t-options='{"widget": "date", "format": "dd/MM/yyyy"}'` to `<span t-field="o.invoice_date"/>`
- [x] 3.2 In line 105, add `t-options='{"widget": "date", "format": "dd/MM/yyyy"}'` to `<span t-field="o.invoice_date_due"/>`
- [x] 3.3 Confirm: print a Thai tax invoice and verify invoice date and due date show `dd/MM/yyyy`

## 4. Rental Contract Template

- [x] 4.1 In `addons/ggg_rental/report/rental_contract_templates.xml` line 42, update `t-options` from `'{"widget": "date"}'` to `'{"widget": "date", "format": "dd/MM/yyyy"}'` on the วันที่ field
- [x] 4.2 In line 77, add `t-options='{"widget": "date", "format": "dd/MM/yyyy"}'` to `<span t-field="doc.rental_start_date"/>`
- [x] 4.3 In line 78, add `t-options='{"widget": "date", "format": "dd/MM/yyyy"}'` to `<span t-field="doc.rental_return_date"/>`
- [x] 4.4 Confirm: print a rental contract and verify the header date and both rental period table cells show `dd/MM/yyyy`
