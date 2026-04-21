## Context

The rental return wizard (`rental.order.wizard`) currently handles quantity selection, serial number selection, late fee generation, stock moves, and automatic deposit credit notes. There is no mechanism for staff to assess product condition or charge damage fees. The deposit credit note is created automatically at full proportional amount in `sale.order.line.write()` when `qty_returned` changes (line 550 of `sale_order_line.py`).

Late fees already follow the pattern of adding a separate service SO line via `_generate_delay_line()`. Damage fees will follow the same pattern.

## Goals / Non-Goals

**Goals:**
- Staff can mark each returned item/serial as good or damaged in the existing return wizard (single step)
- Damaged items generate a "Damage Fee" service SO line with staff-entered amount and reason
- Damage events are logged on `stock.lot` records for serial-tracked products
- Damage history is viewable via smart button on the `stock.lot` form
- Partial returns with mixed conditions work correctly
- Damage fees are uncapped (can exceed deposit amount)
- All returned items go back to normal stock regardless of condition

**Non-Goals:**
- Separate repair/scrap stock location routing for damaged items
- Photo/attachment support on damage records (can be added later)
- Damage fee presets or product-level default damage amounts
- Blocking returns based on damage assessment
- Modifying the deposit refund logic (deposit always refunds in full)

## Decisions

### 1. Damage fee as a separate SO line (not deducted from deposit)

Damage fees are added as a new SO line on the sales order, using a dedicated "Damage Fee" service product. The deposit credit note continues to refund the full proportional amount.

**Why:** Consistent with the existing late fee pattern (`_generate_delay_line`). Cleaner accounting — deposit and damage are separate journal entries. Naturally handles damage > deposit (customer owes the balance). No changes needed to deposit refund logic.

**Alternative considered:** Deducting from deposit credit note amount. Rejected because it couples damage logic into the deposit flow, complicates partial return math, and doesn't handle damage exceeding deposit.

### 2. Condition fields on wizard line (not on SO line)

The `condition`, `damage_fee`, and `damage_reason` fields live on `rental.order.wizard.line` (transient model). They are not persisted on `sale.order.line`.

**Why:** Condition assessment is a point-in-time event during return, not a persistent state on the order line. The damage record is persisted via `rental.damage.log` and the damage fee SO line. Adding fields to `sale.order.line` would be redundant.

### 3. New `rental.damage.log` model linked to `stock.lot`

A dedicated model stores damage history per serial number, linked to the sale order and lot.

**Why:** Enables querying damage history across orders ("which serials have been damaged more than twice?"). Chatter messages on `stock.lot` would not be structured/queryable. For bulk (non-serial) products, the damage log links to `sale.order` only (no lot).

### 4. Dedicated "Damage Fee" service product (company-level setting)

Similar to `extra_product` for delay costs, a `damage_product` field on `res.company` holds the service product used for damage fee SO lines. Auto-created on first use.

**Why:** Consistent with the delay cost product pattern. Allows the product to be configured with appropriate accounting rules.

### 5. Single-step wizard (condition column added to return view)

The condition assessment is done inline in the return wizard — no second step or separate wizard. A `condition` selection field appears for each line when `status='return'`. When set to `damaged`, the fee and reason fields become visible.

**Why:** Minimizes workflow disruption. Staff already use the return wizard; adding a column is simpler than a multi-step flow.

### 6. Damage processing happens in `_apply()` before the SO line write

In `rental_processing.py _apply()`, after the late fee check and before writing `qty_returned`, damage fee lines and damage logs are created. This keeps the processing order clear: late fee → damage fee → stock move → deposit credit.

**Why:** The deposit credit note is triggered by the `write()` on `sale.order.line` (when `qty_returned` changes). Damage SO lines must be created before that write so they appear on the order before invoicing.

## Risks / Trade-offs

**Risk:** Staff enters wrong damage fee amount → no system validation on amount.
**Mitigation:** Damage fee is a regular SO line — staff or manager can edit it on the sales order after the fact. The damage log preserves the original assessed amount for audit.

**Risk:** Bulk products have no serial-level damage tracking.
**Mitigation:** Acceptable — bulk products don't have serial identity. Damage is logged at the order level. If serial tracking is needed, the product should be configured as serial-tracked.

**Risk:** Damage product not configured in company settings on first use.
**Mitigation:** Auto-create pattern (same as delay cost product). Search for existing product with code `DAMAGE`, create if not found.
