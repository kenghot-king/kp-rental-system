## Context

The rental return wizard (`rental.order.wizard`) currently has a `condition` field with two values: `good` and `damaged`. Regardless of condition, `_create_rental_return` always routes returning stock from the Rental Location to `warehouse.lot_stock_id` (WH/Stock). Damage is recorded as a fee SO line and a `rental.damage.log` entry, but the physical stock is not separated — damaged items re-enter rentable stock immediately.

The company model already has `rental_loc_id` (the "in rental" location) with an auto-creation pattern via `_create_per_company_locations`. We extend this pattern to add Inspection and Damage locations.

## Goals / Non-Goals

**Goals:**
- Route returning stock to Damage Location or Inspection Location based on condition chosen at return
- Auto-create Damage Location and Inspection Location per company (same pattern as Rental Location)
- Expose both locations in company settings
- Show fee/reason fields for both `damaged` and `inspect` conditions; charge immediately if fee > 0
- Raise `UserError` when the required location is not configured

**Non-Goals:**
- No new rental order state (`inspect` state is not added)
- No release wizard — staff use standard Odoo stock transfers to move stock out of Inspection/Damage
- No inspection queue or dashboard views
- No changes to deposit credit note logic or late-return logic

## Decisions

### 1. Location auto-creation uses the same pattern as `rental_loc_id`

**Decision:** Add `damage_loc_id` and `inspection_loc_id` to `res.company`. Both are auto-created in `_create_per_company_locations` via a shared helper `_create_rental_support_locations`. A `post_init_hook` creates them for existing companies.

**Why:** Consistent with the existing `rental_loc_id` pattern. Staff can override the auto-created location in settings if they want a custom location hierarchy.

**Alternative considered:** Let users create and assign locations manually (no auto-create). Rejected — too much setup friction for new installs.

### 2. `_create_rental_return` gains a `location_dest_id` parameter

**Decision:** Add an optional `location_dest_id` parameter to `_create_rental_return`. If not supplied, defaults to `warehouse.lot_stock_id` (preserving current behavior).

**Why:** Keeps the method general-purpose. The wizard `_apply` passes the correct destination based on `condition`. No need to duplicate move creation logic.

### 3. Fee/reason shown for both `damaged` and `inspect`; `_process_damage` called for both

**Decision:** The wizard view shows fee/reason fields when `condition in ('damaged', 'inspect')`. `_process_damage` is called for both conditions — it already guards on `fee > 0` before creating any line. The only difference between conditions is the stock destination.

**Why:** Staff may have a preliminary damage estimate at return time even for items going to inspection. Charging immediately avoids a follow-up step. If there's no damage yet, fee = 0 and nothing is created.

### 4. Validation: UserError if location not configured when that condition is selected

**Decision:** In `_apply`, before creating the stock move, check that `company.damage_loc_id` (for damaged) or `company.inspection_loc_id` (for inspect) is set. Raise `UserError` with a clear message directing staff to configure it in Settings.

**Why:** Silent fallback to WH/Stock would defeat the purpose of the feature — staff would think the item was quarantined but it would be immediately rentable.

## Risks / Trade-offs

- **[Risk] Existing damage records have no stock separation** — Prior returns marked `damaged` already landed in WH/Stock. Migration: no automatic fix; staff can manually transfer if needed. → *Mitigation*: Document this in release notes.
- **[Risk] Inspection location not configured on upgrade** — If `inspection_loc_id` is null and a user picks `inspect`, they get a `UserError`. → *Mitigation*: The `post_init_hook` creates locations automatically; settings page prompts configuration.
- **[Trade-off] No `inspect` order state** — Tracking which orders have items in inspection requires querying stock quants at the Inspection Location, not the rental order itself. Accepted per design decision: standard Odoo stock views handle this.

## Migration Plan

1. Module upgrade runs `post_init_hook` → creates Damage and Inspection locations for all companies that don't have them yet.
2. No data migration for historical damage records (items already in WH/Stock stay there).
3. Rollback: remove `damage_loc_id` / `inspection_loc_id` columns; revert wizard `condition` to 2-value selection. No destructive data changes.
