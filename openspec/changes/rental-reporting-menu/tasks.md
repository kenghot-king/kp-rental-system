# Tasks: rental-reporting-menu

## Implementation

- [x] Add `Invoices` and `Payments` menuitem entries to `sale_renting_menus.xml` under `menu_rental_reporting`
- [x] Create `views/rental_invoice_report_views.xml` with:
  - `ir.actions.act_window` for By Item (`account.move.line`)
  - `ir.ui.view` list view with all specified columns
  - `ir.ui.view` search view with Rental filter, payment state filters, and group-by options
- [x] Add By Item menuitem to `sale_renting_menus.xml`
- [x] Register `rental_invoice_report_views.xml` in `__manifest__.py` data list

## QA (manual — install/upgrade module to test)

- [ ] Invoices menu item opens standard invoice list, no errors
- [ ] Payments menu item opens standard payments list, no errors
- [ ] By Item opens with Rental filter active by default — shows only rental invoice lines
- [ ] Removing Rental filter shows all customer invoice lines
- [ ] Rows are flat (no default grouping) — group-by options available in search bar
- [ ] Subtotal column shows sum at bottom
- [ ] Date / Due Date columns visible and sortable
- [ ] Payment state badge shows correct color per state
- [ ] Clicking invoice cell navigates to the invoice form
