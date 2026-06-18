# Design: rental-reporting-menu

## Menu Structure

```
Rental
└── Reporting
    ├── Rental Analysis          (existing, action_rental_report)
    ├── Invoices                 (new — account.action_move_out_invoice_type)
    ├── Payments                 (new — account.action_account_payments)
    └── By Item                  (new — custom action on account.move.line)
```

## Invoices & Payments Menu Items

These are thin `<menuitem>` entries that reference existing `account` module actions directly. No view duplication — Odoo reuses the standard list/form views. Users get the full invoice/payment UI including filters, group-by, and click-through to forms.

```xml
<menuitem id="menu_rental_reporting_invoices"
    name="Invoices"
    parent="menu_rental_reporting"
    action="account.action_move_out_invoice_type"
    sequence="10"/>

<menuitem id="menu_rental_reporting_payments"
    name="Payments"
    parent="menu_rental_reporting"
    action="account.action_account_payments"
    sequence="20"/>
```

## By Item View

### Model: `account.move.line`

No custom model needed. `account.move.line` has all required fields:

| Column | Field | Note |
|---|---|---|
| Invoice # | `move_id` (name) | Many2one to account.move |
| Invoice Date | `move_id.invoice_date` | via related |
| Due Date | `move_id.invoice_date_due` | via related |
| Customer | `partner_id` | direct field |
| Product | `product_id` | direct field |
| Description | `name` | line description |
| Qty | `quantity` | direct field |
| Unit Price | `price_unit` | direct field |
| Subtotal | `price_subtotal` | direct field |
| Status | `parent_state` | stored on move.line: draft/posted/cancel |
| Payment State | `move_id.payment_state` | via related, stored |

### Domain Filter (default)

Filter to lines that belong to rental customer invoices:

```python
domain = [
    ('move_id.move_type', '=', 'out_invoice'),
    ('move_id.invoice_line_ids.sale_line_ids.order_id.is_rental_order', '=', True),
    ('display_type', '=', 'product'),  # exclude section/note lines
]
```

> The `is_rental_order` filter is a default search filter (named "Rental"), not a hard domain on the action — so users can remove it to see all invoices.

### Action Domain (hard)

The action domain only restricts to `out_invoice` lines and `product` display type. The "Rental" filter is a `search_default_*` context key so it can be toggled off.

```python
action domain: [('move_id.move_type', '=', 'out_invoice'), ('display_type', '=', 'product')]
action context: {'search_default_rental': 1}  # no default group_by
```

### Default Group-by

No default grouping — flat list of line items. Users can apply group-by manually via the search bar if needed.

### Search Filters

- **Rental** (default on): filter lines to invoices linked to rental orders
- **Date**: filter by `move_id.invoice_date`
- **Status**: filter by `parent_state` (Posted / Draft)
- **Payment State**: filter by `move_id.payment_state` (Paid / In Payment / Not Paid)
- **Customer**: existing `partner_id` search

## Access

Visible to `sales_team.group_sale_manager` (same as existing Reporting menu) for Invoices, Payments, and By Item. No new security groups needed.
