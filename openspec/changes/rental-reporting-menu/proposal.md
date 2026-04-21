## Why

The Rental Reporting menu today shows only the Rental Analysis chart. Staff and managers cannot access invoice or payment data from within the Rental app — they have to navigate to the Invoicing module and filter manually. This change adds three reporting views directly in the Rental menu: the standard Invoices list, the standard Payments list, and a new "By Item" view that expands each invoice into its line items for product-level visibility.

## What Changes

- Add **Invoices** menu item in Rental → Reporting — points to the standard `account` module customer invoices action (`account.action_move_out_invoice_type`)
- Add **Payments** menu item in Rental → Reporting — points to the standard `account` module customer payments action (`account.action_account_payments`)
- Add **By Item** menu item in Rental → Reporting — new `ir.actions.act_window` on `account.move.line`, filtered to lines belonging to rental customer invoices, showing invoice header + line detail columns, default group-by invoice
- Default filter on By Item: rental invoices only (lines whose invoice is linked to a rental sale order), removable by the user

## Capabilities

### New Capabilities
- `rental-reporting-menu`: Three reporting views (Invoices, Payments, By Item) accessible from Rental → Reporting

## Impact

- `sale_renting_menus.xml` — add three `<menuitem>` entries under `menu_rental_reporting`
- New view XML file — `ir.actions.act_window` + `ir.ui.view` (list) for By Item on `account.move.line`
- No new Python models — the view uses existing `account.move.line` fields plus stored relational fields (`move_id`, `partner_id`, `product_id`, etc.)
- No changes to existing views or models
