## Why

When customers return rental products, all items go directly back to warehouse stock and become immediately rentable — even if staff need to inspect them or they are visibly damaged. This means damaged or suspect items can be re-rented before being assessed, creating liability and quality issues.

## What Changes

- Add two new stock locations per company: **Inspection Location** and **Damage Location** (auto-created on company setup, configurable in settings).
- Extend the return wizard `condition` field from 2 choices (Good / Damaged) to 3 choices (Good / Damaged / Inspect).
- Route returned stock to the correct location based on condition:
  - **Good** → Warehouse Stock (immediately rentable, current behavior)
  - **Damaged** → Damage Location (removed from rental availability)
  - **Inspect** → Inspection Location (removed from rental availability, pending review)
- For **Damaged** and **Inspect** conditions, staff may enter a damage fee (can be 0) and reason at return time — fee is charged immediately if > 0.
- Raise `UserError` if the required location (Damage or Inspection) is not configured when that condition is used.
- No new rental order states — the order completes normally. Inspection and damage stock tracking is handled via standard Odoo stock transfers.

## Capabilities

### New Capabilities
- `return-condition-routing`: Condition-based stock routing at return time (Good/Damaged/Inspect → correct location), with immediate fee charging for Damaged and Inspect conditions.
- `rental-return-locations`: Company-level configuration for Damage Location and Inspection Location, with auto-creation on company setup.

### Modified Capabilities

## Impact

- **Models**: `res.company` (+`damage_loc_id`, +`inspection_loc_id`), `res.config.settings` (mirrored fields)
- **Wizard**: `rental.order.wizard.line` — `condition` gains `inspect`, fee/reason shown for both `damaged` and `inspect`, `_apply` routes stock by condition
- **`sale_order_line.py`**: `_create_rental_return` gains `location_dest_id` parameter
- **Views**: Return wizard form (condition field, fee/reason visibility), Settings form (two new location fields)
- **No state machine changes**, no new transient models
