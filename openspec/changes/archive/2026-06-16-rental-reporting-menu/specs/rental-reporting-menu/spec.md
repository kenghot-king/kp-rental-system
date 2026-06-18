# Spec: rental-reporting-menu

## Invoices Menu Item

- A `<menuitem>` under `menu_rental_reporting` named **Invoices**, sequence 10
- Action: `account.action_move_out_invoice_type` (standard Invoicing module action)
- Visible to `sales_team.group_sale_manager`
- Opens the standard customer invoices list/form

## Payments Menu Item

- A `<menuitem>` under `menu_rental_reporting` named **Payments**, sequence 20
- Action: `account.action_account_payments` (standard account module action)
- Visible to `sales_team.group_sale_manager`
- Opens the standard payments list/form

## By Item View

### Action
- Model: `account.move.line`
- View type: list (default), no form override needed (click-through uses native `account.move.line` form or redirects to parent invoice)
- Hard domain: `[('move_id.move_type', '=', 'out_invoice'), ('display_type', '=', 'product')]`
- Context:
  - `search_default_rental: 1` — activates Rental filter by default
  - No default group-by — flat list

### List View Columns (in order)

| Label | Field | Widget/Options |
|---|---|---|
| Invoice | `move_id` | link to invoice form |
| Date | `move_id.invoice_date` | date |
| Due Date | `move_id.invoice_date_due` | date |
| Customer | `partner_id` | |
| Product | `product_id` | |
| Description | `name` | optional (hidden by default) |
| Qty | `quantity` | |
| Unit Price | `price_unit` | monetary |
| Subtotal | `price_subtotal` | monetary, sum |
| Status | `parent_state` | badge: posted=success, draft=warning, cancel=danger |
| Payment | `move_id.payment_state` | badge |
| Currency | `currency_id` | invisible (used by monetary widgets) |

### Search View Filters

| Name | Key | Domain/Context |
|---|---|---|
| Rental | `search_default_rental` | `move_id.invoice_line_ids.sale_line_ids.order_id.is_rental_order = True` |
| Paid | — | `move_id.payment_state = 'paid'` |
| In Payment | — | `move_id.payment_state = 'in_payment'` |
| Not Paid | — | `move_id.payment_state = 'not_paid'` |

### Search View Group-by Options

- Invoice (`move_id`)
- Customer (`partner_id`)
- Product (`product_id`)
- Invoice Date (`move_id.invoice_date`, by month)
- Payment State (`move_id.payment_state`)

### Menu Item

- Name: **By Item**
- Parent: `menu_rental_reporting`
- Sequence: 30
- Groups: `sales_team.group_sale_manager`
