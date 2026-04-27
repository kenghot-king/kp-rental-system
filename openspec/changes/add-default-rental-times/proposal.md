## Why

Rental orders currently default the return time to whatever raw 24h math produces (e.g., pickup May 1 09:00 + 5 days → return May 6 09:00). This conflicts with how the business actually counts rental periods — by calendar day-spans with end-of-day return deadlines. Operators have to manually adjust pickup and return times on every order, which is tedious and error-prone. Two company-level defaults (pickup time and return time) let the system align with the business model out of the box.

## What Changes

- Add `default_pickup_time` field on `res.company` (Float, hours since midnight, default `9.0` = 09:00).
- Add `default_return_time` field on `res.company` (Float, hours since midnight, default `23.983` ≈ 23:59).
- Surface both fields in **Rental → Configuration → Settings**, inside the existing **Default Delay Costs** section.
- When a rental order's pickup or return date is set without a time component (or with a default time provided by the date picker), apply the corresponding configured default time.
- Respect manual edits: if the user explicitly sets a time, do not overwrite it with the default.

## Capabilities

### New Capabilities
- `rental-default-times`: Company-level configuration for the default time component applied to rental order pickup and return dates.

### Modified Capabilities
<!-- None — this is purely additive configuration. -->

## Impact

- **Models:** New fields on `res.company` (in `addons/ggg_rental/models/res_company.py`).
- **Settings UI:** New fields in `addons/ggg_rental/models/res_config_settings.py` (related fields on `res.config.settings`) and in `addons/ggg_rental/views/res_config_settings_views.xml` (Default Delay Costs section).
- **Order behavior:** A small onchange/compute hook on `sale.order` (in `addons/ggg_rental/models/sale_order.py`) snaps the time component of `rental_start_date` and `rental_return_date` to the configured defaults when only a date is provided.
- **Migration:** Existing companies need the new fields populated with defaults — handled by Odoo's standard field default on next module update.
- **No breaking changes**: existing orders are untouched; defaults only apply on new date-without-time input.
