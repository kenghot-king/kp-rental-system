# Tasks: rental-contract-print

- [x] 1. Add `rental_contract_terms` Html field to `res.company` (company-dependent, under `# Rental Contract` section)
- [x] 2. Add related `rental_contract_terms` field to `res.config.settings`; expose in `res_config_settings_views.xml` as a rich-text widget under a new "Rental Contract" section
- [x] 3. Add `action_print_rental_contract()` to `sale.order`: raise `UserError` if `self.rental_status not in ('pickup', 'return', 'returned')`; otherwise trigger the new report action
- [x] 4. Create `report/rental_contract_templates.xml` with `report_rental_contract_document` and `report_rental_contract` QWeb templates per the design
- [x] 5. Add `ir.actions.report` record ("Rental Contract") to `rental_report_views.xml` — `report_type=qweb-pdf`, bound to `sale.order`, no `binding_type` (triggered by button, not Print menu)
- [x] 6. Add "Print Contract" button to the rental order form view (`sale_order_views.xml`), visible when `is_rental_order = True`, calls `action_print_rental_contract`
- [x] 7. Add `report/rental_contract_templates.xml` to `__manifest__.py` data list
