## Why

Odoo's Rental module (`sale_renting`) and its dependency Gantt view (`web_gantt`) are Enterprise-only (OEEL-1 license). We need a full-featured rental management system running on Odoo 19 Community Edition without Enterprise licensing. The Enterprise modules serve as architectural reference for a clean-room rewrite under LGPL-3.

## What Changes

- **New `ggg_gantt` addon**: Community Gantt chart view providing CSS Grid-based timeline visualization with drag-drop, resize, dependency connectors, virtual scrolling, progress bars, and unavailability display. Registers `gantt` as a new view type usable by any Odoo model.
- **New `ggg_rental` addon**: Full rental management application — rentable product configuration, duration-based pricing engine with best-price selection, rental order workflow (quote → confirm → pickup → return), pickup/return wizard, late fee auto-generation, rental schedule Gantt view, and rental analytics reporting.
- **New dependency chain**: `web` → `ggg_gantt` → `ggg_rental` ← `sale` (all Community modules).

## Capabilities

### New Capabilities

- `gantt-view`: Reusable Gantt chart view type — Python backend (`get_gantt_data` API, dependency-aware rescheduling, cycle detection), JS frontend (MVC with arch parser, model, renderer, controller), CSS Grid rendering with virtual scrolling, pill drag/resize/connect interactions, popovers, scale selector, progress bars, and unavailability display.
- `rental-pricing`: Duration-based rental pricing engine — temporal recurrences (hour/day/week/month/year + overnight), pricing rules per product/variant/pricelist, PERIOD_RATIO unit conversion with ceiling rounding, best-price selection algorithm across multiple rules.
- `rental-orders`: Rental order management — `is_rental` flag on SO/SOL, rental date period (start/return), rental status machine (draft → pickup → return → returned), `is_late` detection, date validation, price recalculation on duration change, Gantt schedule integration via `web_gantt_write`.
- `rental-operations`: Pickup and return workflow — transient wizard for processing pickup/return quantities, partial pickup/return support, late fee calculation (grace period + hourly/daily rates), automatic delay service line generation, chatter logging.
- `rental-products`: Rental product configuration — `rent_ok` toggle on product templates, rental pricing rules tab, `qty_in_rent` tracking, `display_price` computation, extra hourly/daily fee fields, combo product rental constraints.
- `rental-reporting`: Rental analytics — SQL view expanding rentals to daily records, pivot/graph views for quantity and revenue analysis over time.

### Modified Capabilities

_(none — all new capabilities on a fresh Community installation)_

## Impact

- **New addons**: `addons/ggg_gantt/` and `addons/ggg_rental/` created from scratch
- **Odoo dependencies**: Extends core models (`base`, `ir.ui.view`, `ir.actions.act_window.view`, `product.template`, `product.product`, `product.pricelist`, `sale.order`, `sale.order.line`, `res.company`, `res.config.settings`)
- **New models**: `sale.temporal.recurrence`, `product.pricing`, `rental.order.wizard`, `rental.order.wizard.line`, `sale.rental.report`
- **New view type**: `gantt` registered in view and action registries
- **Frontend assets**: ~7000L JS (Gantt) + ~500L JS (Rental) added to `web.assets_backend` / `web.assets_backend_lazy`
- **No breaking changes**: Entirely additive — installs alongside existing Community modules
