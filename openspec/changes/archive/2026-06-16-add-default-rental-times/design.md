## Context

Odoo's standard rental flow stores `rental_start_date` and `rental_return_date` as `Datetime` fields on `sale.order`. When a user picks a date in the UI, the date picker assigns a default time (typically the user's current time or a framework default). For this rental business, that default is wrong — pickup should default to shop opening time (09:00) and return should default to end-of-day (23:59).

The existing **Rental → Configuration → Settings** screen already exposes a "Default Delay Costs" section backed by fields on `res.company` (`extra_hour`, `extra_day`, `min_extra_hour`, `extra_product`). The new defaults belong in the same section per the user's request.

## Goals / Non-Goals

**Goals:**
- Two configurable company-level fields for default pickup time and default return time.
- Surfaced in the existing "Default Delay Costs" section of Rental Settings.
- Sensible defaults out of the box (09:00 pickup, 23:59 return).
- Snap behavior when a date is set without an explicit time.
- Respect manual edits — no overwriting after the user has set a time.

**Non-Goals:**
- Per-product time overrides (deferred — see `documents/to-do/default-rental-period-times.md`).
- Calendar-day vs 24h pricing toggle (deferred).
- Late pickup / late return policy logic (deferred).
- Any change to the delay-cost formula or grace-period logic.
- Pricing-rule lookup behavior (separate concern, parked).

## Decisions

### D1. Storage type: `Float` (hours since midnight)

Use `Float` with `widget="float_time"` for both fields. This matches Odoo's convention for time-of-day fields (e.g., `resource.calendar.attendance.hour_from/hour_to`). Values are hours as decimals: `9.0` = 09:00, `23.983333` ≈ 23:59.

**Alternatives considered:**
- `Char` ("HH:MM"): more readable in DB but requires parsing on every read.
- Two integer fields (hour + minute): more code, no benefit.

Float wins on convention and built-in widget support.

### D2. Defaults: `9.0` and `23.983333`

- `default_pickup_time = 9.0` → 09:00 (typical shop opening)
- `default_return_time = 23.983333` → 23:59 (end of day, matches the user's day-span business model)

**Alternatives considered:**
- `default_return_time = 24.0` (midnight): conceptually "end of day" but may roll into next day in some date math. 23:59 avoids ambiguity.

### D3. Snap behavior: onchange on `sale.order`

Add an `@api.onchange('rental_start_date', 'rental_return_date')` hook that, for each datetime field that was set with a default time component (e.g., 00:00:00 from a date-only picker), replaces the time portion with the configured default. Do not snap if the time is already non-default.

**Alternatives considered:**
- Override `default_get`: only fires once at record creation; misses subsequent date edits.
- Compute field with inverse: harder to reason about for users; changes field stored value silently.
- Server-side write override: too aggressive — would re-snap on every save.

Onchange runs in the form view only, gives the user immediate visual feedback, and is the most common Odoo pattern for this kind of UX nudge.

### D4. "Already set" detection: time component == 00:00:00

The simplest signal that the user only picked a date (and the picker filled in midnight) is that the time portion equals `00:00:00`. If the time is anything else, assume the user explicitly chose it and don't override.

**Edge case acknowledged:** if a user actually wants a 00:00 pickup, the system will overwrite it to 09:00. This is judged acceptable — midnight pickups are vanishingly rare for a daytime rental shop, and the user can always re-edit the time after the snap.

### D5. Placement in the existing Default Delay Costs section

The user explicitly chose this placement. While the new fields are not strictly about *delay*, grouping them in the same section keeps the settings page compact and avoids creating a single-purpose section. The section header may be renamed in a future change if more period-related defaults are added.

## Risks / Trade-offs

- **[Snap overwrites a deliberate 00:00 time]** → Mitigation: documented in user-facing help text on the field; user can re-edit immediately after.
- **[Existing in-flight orders untouched]** → By design — defaults apply only to new date-without-time input. No migration risk.
- **[Confusion: "Default Delay Costs" now contains non-delay fields]** → Mitigation: clear field labels ("Default Pickup Time", "Default Return Time"). Section can be renamed in a follow-up.
- **[User TZ vs server TZ]** → Datetime fields are stored in UTC; the snap must be applied in the user's timezone, then converted. Use `fields.Datetime.context_timestamp` and timezone-aware arithmetic.

## Migration Plan

1. Add fields to `res.company` with Python-level defaults (`default=9.0` and `default=23.983333`).
2. On module update, all existing companies automatically get the defaults populated by Odoo's standard field-default mechanism — no migration script needed.
3. No backfill of existing orders; defaults apply only to newly-entered date-without-time inputs.
4. Rollback: revert the module; fields become orphaned columns (harmless), can be dropped with a follow-up `_cleanup` migration if needed.

## Open Questions

None for this scope. Open questions about edge cases (sub-day rentals, per-product overrides, late pickup policy) are tracked in `documents/to-do/default-rental-period-times.md` under "Parked for later".
