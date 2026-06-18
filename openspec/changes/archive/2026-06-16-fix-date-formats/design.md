## Context

The rental system runs on Odoo 19 CE with a Thai business context. All dates are currently rendered using Odoo's locale-dependent "short" format via Babel. When users' language is `en_US` (common for admin/developer accounts), Babel's short format outputs `M/D/YY HH:MM AM/PM` — American style. The required display format is `dd/MM/yyyy` for dates and `dd/MM/yyyy HH:mm` (24h) for datetimes, unconditionally.

The problem exists in two separate layers:
1. **Model layer** — `_get_rental_order_line_description()` uses Python `format_datetime`/`format_time` from `odoo.tools`, which delegates to Babel with `dt_format='short'`.
2. **Template layer** — QWeb `<span t-field="...">` fields without `t-options` use Odoo's default locale-based rendering.

## Goals / Non-Goals

**Goals:**
- All date/datetime values displayed in rental reports and contracts render in `dd/MM/yyyy` or `dd/MM/yyyy HH:mm` format regardless of the logged-in user's language.
- The rental order line description (shown in UI and sale order print) renders the rental period in the correct format.

**Non-Goals:**
- Changing date display in non-rental Odoo modules (invoices outside `report_invoice_thai.xml`, standard sale reports, etc.).
- Changing the storage format of any field.
- Changing time zone handling — timezone conversion logic is unchanged.

## Decisions

### D1 — Explicit format strings over locale configuration

**Decision:** Hardcode `'dd/MM/yyyy, HH:mm'` in `format_datetime` calls and add `t-options` with `"format": "dd/MM/yyyy"` / `"format": "dd/MM/yyyy HH:mm"` in QWeb templates rather than switching the Odoo system language to `th_TH`.

**Rationale:** Setting `th_TH` locale would also switch number separators, currency symbols, and Buddhist calendar year (B.E. 2569 instead of 2026), which is undesired. Explicit format strings are locale-independent and predictable for every user account.

**Alternative considered:** Set language to `en_GB` (which gives `dd/MM/yyyy`). Rejected — still locale-dependent and fragile if locale data changes between Odoo versions.

### D2 — Format date-only fields with `"widget": "date"`, datetimes with `"widget": "datetime"`

**Decision:** In QWeb templates, use `{"widget": "date", "format": "dd/MM/yyyy"}` for `Date` fields and `{"widget": "datetime", "format": "dd/MM/yyyy HH:mm"}` for `Datetime` fields.

**Rationale:** Using the correct widget ensures Odoo applies timezone conversion (for datetime) and avoids rendering artifacts. The `format` key overrides the locale format while keeping all other widget behaviour intact.

### D3 — Model description uses `HH:mm` (24h), no seconds

**Decision:** `_get_rental_order_line_description()` uses `'dd/MM/yyyy, HH:mm'` for full datetime parts and `'HH:mm'` for time-only (same-day return).

**Rationale:** Seconds are irrelevant in a rental context. The format matches what prints in the rental contract, keeping UI and document consistent.

## Risks / Trade-offs

- **Existing stored descriptions not updated** → Line names already saved in `sale.order.line.name` still contain the old format. They will only refresh when the order dates are changed or the line is reset. For production data, a one-time migration script or manual reconfirmation of orders may be needed. Low risk for pre-launch system.
- **Babel format string compatibility** → `format_datetime` in `odoo.tools.misc` accepts ICU/Babel pattern strings. `'dd/MM/yyyy, HH:mm'` is a valid Babel pattern. No risk of breakage.
- **QWeb `format` key support** → Odoo 17+ QWeb supports the `format` key in `t-options` for date/datetime widgets. Confirmed available in Odoo 19.

## Migration Plan

1. Deploy code changes (model + templates).
2. Existing sale order line descriptions keep old format until their order's dates are touched — no automated migration needed pre-launch.
3. No rollback complexity: the change is purely cosmetic (display format only); reverting restores old locale-based rendering.

## Open Questions

<!-- None outstanding -->
