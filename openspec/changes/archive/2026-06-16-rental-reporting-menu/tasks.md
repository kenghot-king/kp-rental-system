# Tasks: rental-reporting-menu

## Implementation

- [X] Add `Invoices` and `Payments` menuitem entries to `sale_renting_menus.xml` under `menu_rental_reporting`
- [X] Create `views/rental_invoice_report_views.xml` with:
  - `ir.actions.act_window` for By Item (`account.move.line`)
  - `ir.ui.view` list view with all specified columns
  - `ir.ui.view` search view with Rental filter, payment state filters, and group-by options
- [X] Add By Item menuitem to `sale_renting_menus.xml`
- [X] Register `rental_invoice_report_views.xml` in `__manifest__.py` data list

## QA (manual — install/upgrade module to test)

- [X] Invoices menu item opens standard invoice list, no errors
- [X] Payments menu item opens standard payments list, no errors
- [X] By Item opens with Rental filter active by default — shows only rental invoice lines
- [X] Removing Rental filter shows all customer invoice lines
- [X] Rows are flat (no default grouping) — group-by options available in search bar
- [X] Subtotal column shows sum at bottom
- [X] Date / Due Date columns visible and sortable
- [X] Payment state badge shows correct color per state
- [X] Clicking invoice cell navigates to the invoice form
