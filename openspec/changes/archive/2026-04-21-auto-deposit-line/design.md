## Context

Currently, deposit lines on rental orders are created manually. The system has an `is_rental_deposit` flag on `product.template` and downstream logic for invoice splitting and credit notes on return, but no automation for deposit line creation.

The existing settings pattern on `res.company` / `res.config.settings` already has fields like `extra_product`, `damage_product`, and `deposit_auto_refund`. This change adds a `rental_deposit_product_id` field alongside them.

Key existing code:
- `sale_order_line.py` — `_compute_is_rental()` determines rental lines; `write()` handles pickup/return stock + deposit credit notes
- `sale_order.py` — `_create_invoices()` splits deposit vs non-deposit invoices
- `res_company.py` — company-level rental config fields
- `res_config_settings.py` — settings UI wrappers

## Goals / Non-Goals

**Goals:**
- Auto-create a deposit line when a rental product is added to an SO
- Keep deposit line qty synced with the parent rental line qty
- Auto-remove deposit line when the parent rental line is removed
- Make deposit lines read-only in the UI
- Raise `UserError` if no deposit product is configured when adding a rental product
- Plug into existing invoice splitting and credit note logic seamlessly

**Non-Goals:**
- Per-product deposit amounts (all deposits use the rental product's `list_price`)
- Per-product deposit product linking (single company-level deposit product)
- Changing the existing deposit credit note or invoice splitting behavior
- Deposit lines for non-rental products

## Decisions

### 1. Company-level deposit product configuration

Add `rental_deposit_product_id` (Many2one → `product.product`) on `res.company` with domain `[('is_rental_deposit', '=', True)]`. Expose via `res.config.settings` as a related field.

**Why not per-product?** Simpler setup, single source of truth. The existing pattern (`extra_product`, `damage_product`) is company-level. Can be extended later if needed.

**Why not search for first `is_rental_deposit` product?** Explicit config avoids ambiguity when multiple deposit products exist and makes the admin's intent clear.

### 2. Link via `deposit_parent_id` on `sale.order.line`

Add `deposit_parent_id` (Many2one → `sale.order.line`, ondelete='cascade') to link deposit lines back to their parent rental line.

**Why cascade delete?** When the rental line is removed, the deposit line should be removed automatically. Cascade handles this at the ORM level without extra code.

**Why not a reverse One2many on the parent?** We only ever need one deposit line per rental line. The Many2one on the child is sufficient and simpler.

### 3. Deposit line creation trigger

Override `write()` and `create()` on `sale.order.line` to detect when a rental product is set and auto-create the deposit line. Specifically:
- In `create()`: if the line is rental (`is_rental` context + `rent_ok` product), create the deposit line
- On product change: handled via `@api.onchange('product_id')` or `write()` override

The deposit line values:
- `product_id`: `company.rental_deposit_product_id`
- `name`: `[Deposit] {product.name}`
- `price_unit`: rental product's `list_price`
- `product_uom_qty`: same as parent line
- `deposit_parent_id`: parent line ID
- `tax_id`: copied from the rental line's taxes (ensures deposit has same tax treatment as the rented product)
- `is_rental`: False (deposit is a service, not a rental line)

### 4. Quantity sync via computed field

Make `product_uom_qty` on deposit lines follow the parent via `@api.depends('deposit_parent_id.product_uom_qty')`. When the parent qty changes, the deposit qty recomputes automatically.

**Alternative considered:** Override `write()` to propagate qty changes. Rejected because a computed dependency is more declarative and less error-prone.

**Implementation note:** Since `product_uom_qty` is a standard Odoo field with existing compute logic, we need to extend the existing compute method rather than replacing it. For deposit lines (where `deposit_parent_id` is set), override to follow the parent. For all other lines, delegate to `super()`.

### 5. Read-only enforcement at UI level

Use `readonly` attribute in the XML view with `deposit_parent_id` as the condition. Fields to lock: `product_id`, `product_uom_qty`, `price_unit`, `name`.

**Why not model-level constraint?** UI-level is sufficient — the sync logic owns the values programmatically. A model constraint would complicate the auto-creation code itself.

### 6. UserError on missing config

In the deposit line creation logic, if `company.rental_deposit_product_id` is not set, raise `UserError` with a message directing the admin to configure the deposit product in Settings. This blocks adding any rental product to an SO until configuration is done.

## Risks / Trade-offs

**[Risk] Existing orders with manual deposit lines** → No migration needed. Existing deposit lines lack `deposit_parent_id` and continue to work as before. Only new rental lines trigger auto-creation.

**[Risk] `product_uom_qty` computed override conflicts with standard Odoo logic** → Mitigated by only overriding for lines where `deposit_parent_id` is set. All other lines use standard behavior.

**[Risk] Cascade delete removes deposit line mid-invoice** → Low risk. Rental lines are only deleted in draft/quote state. Once confirmed, Odoo prevents line deletion.

**[Trade-off] Single deposit product for all rentals** → Simpler but less flexible. Acceptable for current requirements; can be extended to per-product deposit later.
