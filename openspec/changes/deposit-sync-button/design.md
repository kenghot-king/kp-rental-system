## Context

The `auto-deposit-line` change attempted automatic deposit line creation via `@api.onchange` and `write()` overrides. This was unreliable because Odoo's virtual `NewId` records made it impossible to reliably match parent ↔ child deposit lines, resulting in duplicates and orphaned lines.

Existing infrastructure already in place (from `auto-deposit-line`):
- `rental_deposit_product_id` on `res.company` / `res.config.settings` — company-level deposit product config
- `deposit_parent_id` (Many2one → `sale.order.line`, cascade) — links deposit lines to parent rental lines
- Readonly attrs on deposit lines in SO form view
- `is_rental_deposit` flag on `product.template`
- Invoice splitting and credit note logic for deposit lines

## Goals / Non-Goals

**Goals:**
- Provide a [Sync Deposits] button that reliably creates/updates/removes deposit lines on saved rental orders
- Validate deposit correctness before Send, Print, Confirm, Preview actions via a wizard
- Use product `list_price` (sale price) for deposit amounts

**Non-Goals:**
- Auto-creating deposits without user action (explicitly abandoned)
- Modifying existing invoice split or credit note logic
- Per-product deposit product configuration

## Decisions

### 1. Sync Deposits button placement

Place above the order lines section (not in the header). The button operates on order lines, so it belongs near them. Only visible on rental orders in draft/sent state.

### 2. Sync logic as a single `action_sync_deposits()` method on `sale.order`

The method:
1. Validates `rental_deposit_product_id` is configured (raises `UserError` if not)
2. Removes deposit lines whose parent rental line no longer exists (orphans)
3. Updates existing deposit lines where qty or price has drifted
4. Creates new deposit lines for rental lines that don't have one yet

Uses `deposit_parent_id` for matching (reliable on saved records — no `NewId` issues). All operations happen on real DB records.

### 3. Deposit line values

- `product_id`: `company.rental_deposit_product_id`
- `name`: `[Deposit] {rental_product.name}`
- `price_unit`: `rental_product.list_price` (the sale price / asset value, not the rental rate)
- `product_uom_qty`: same as parent rental line
- `tax_ids`: copied from the rental line's taxes
- `deposit_parent_id`: parent rental line
- `sequence`: `parent.sequence + 1` (positions deposit right after its rental line)

### 4. Validation check — `_check_deposit_sync()`

A read-only method that returns a mismatch list. Checks each rental line:
- Has a deposit child line?
- Deposit qty matches rental qty?
- Deposit price matches product `list_price`?

Returns `False` if everything is in sync, or a list of mismatch descriptions if not.

### 5. Wizard for validation popup

A transient model `rental.deposit.sync.wizard` with:
- `order_id` (Many2one → `sale.order`)
- `original_action` (Char) — the action the user was trying to perform (e.g. `action_confirm`)
- `mismatch_info` (Text) — human-readable description of what's out of sync
- Three buttons:
  - **[Update & Continue]**: calls `action_sync_deposits()` then the original action
  - **[Continue As-Is]**: calls the original action directly
  - **[Cancel]**: closes the wizard

### 6. Intercepting Send, Print, Confirm, Preview

Override each action method on `sale.order`. Before calling `super()`, run `_check_deposit_sync()`. If mismatches found, return the wizard action instead of proceeding.

- `action_quotation_send` → Send
- `action_report_print` or similar → Print
- `action_confirm` → Confirm
- `action_preview_sale_order` or similar → Preview

Cancel is NOT intercepted — closing an order doesn't need deposit validation.

**Alternative considered:** Using `confirm` attribute on the button XML for a simple JS confirm dialog. Rejected because we need to show specific mismatch details and offer "Update & Continue".

## Risks / Trade-offs

**[Risk] User forgets to click Sync Deposits** → Mitigated by the validation wizard on all forward-progressing actions. The wizard catches any drift.

**[Risk] Print action may vary by Odoo version** → Need to verify the exact method name for the Print button in Odoo 19.

**[Trade-off] Two clicks instead of automatic** → Acceptable. Reliability and user control outweigh the convenience of auto-sync. The previous auto approach proved too fragile.

**[Trade-off] Deposit price uses list_price, not rental price** → This is intentional. Deposit reflects asset value. If list_price is 0 or not set, the deposit amount will be 0 — admin should ensure list_price is set on rental products.
