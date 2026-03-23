# GGG Rental - Community Edition Roadmap

> Rewriting Odoo 19 Enterprise `web_gantt` and `sale_renting` as community modules: `ggg_gantt` and `ggg_rental`.

---

## Overview

| Module | Source (Enterprise) | Target (Community) | Depends |
|--------|--------------------|--------------------|---------|
| Gantt View | `web_gantt` | `ggg_gantt` | `web` |
| Rental App | `sale_renting` | `ggg_rental` | `sale`, `ggg_gantt` |

**License**: LGPL-3 (Community compatible)

---

## Phase 1: ggg_gantt (Foundation)

The Gantt chart view is a prerequisite for the rental schedule. It must be fully functional before `ggg_rental` can be built.

### 1.1 Python Backend

| Task | Description | Source Reference | Est. Lines |
|------|-------------|-----------------|------------|
| **1.1.1** Base mixin | `get_gantt_data()` API on `base` model - fetches grouped records, unavailabilities, progress bars for a date range | `web_gantt/models/models.py` | ~300 |
| **1.1.2** Reschedule engine | `web_gantt_reschedule()` - dependency-aware rescheduling with cycle detection, cascading updates, undo support | `web_gantt/models/models.py` | ~300 |
| **1.1.3** View validation | Extend `ir.ui.view` to validate `<gantt>` arch XML against allowed attributes | `web_gantt/models/ir_ui_view.py` | ~120 |
| **1.1.4** Action type | Register `gantt` as a valid view type in `ir.actions.act_window.view` | `web_gantt/models/ir_actions.py` | ~10 |

### 1.2 JavaScript Frontend

| Task | Description | Source Reference | Est. Lines |
|------|-------------|-----------------|------------|
| **1.2.1** Arch parser | Parse `<gantt>` XML into JS config (scales, ranges, fields, permissions, decorations) | `gantt_arch_parser.js` | ~360 |
| **1.2.2** Model | Data layer - fetch via `get_gantt_data()`, generate rows/pills, handle reschedule/copy/dependency CRUD | `gantt_model.js` | ~1160 |
| **1.2.3** Renderer | CSS Grid layout with virtual scrolling, pill rendering, drag/resize/connect interactions, popovers | `gantt_renderer.js` | ~3500 |
| **1.2.4** Controller | View lifecycle, search integration, dialog management, pager, create actions | `gantt_controller.js` | ~220 |
| **1.2.5** Helpers | Date math, grid position utilities, popover management, draggable/resizable hooks | `gantt_helpers.js` | ~890 |
| **1.2.6** Connectors | SVG Bezier dependency lines between pills, create/delete connector interactions | `gantt_connector.js` | ~290 |
| **1.2.7** Sub-components | Popover, scale selector, progress bar, time badge, multi-selection buttons, renderer controls | 7 JS + 7 XML files | ~400 |
| **1.2.8** View registration | Register `ganttView` in Odoo's view registry with MVC wiring | `gantt_view.js` | ~70 |

### 1.3 Styling

| Task | Description | Source Reference |
|------|-------------|-----------------|
| **1.3.1** Core SCSS | Grid layout, pill colors (12-color system), hover/drag states, unavailability cells | `gantt_view.scss` |
| **1.3.2** Variables | Theme variables (border colors, highlight colors, z-index layers) | `gantt_view.variables.scss` |
| **1.3.3** Popover styles | Popover component styling | `gantt_popover.scss` |
| **1.3.4** Dark mode *(optional)* | Dark mode variable overrides and styles | `*.dark.scss` |

### 1.4 Module Scaffolding

| Task | Description |
|------|-------------|
| **1.4.1** `__manifest__.py` | Module metadata, depends=['web'], LGPL-3 license, asset registration |
| **1.4.2** `__init__.py` | Model imports |
| **1.4.3** Security | Access rights (if any beyond inherited) |

### 1.5 Verification

| Task | Description |
|------|-------------|
| **1.5.1** Install test | Module installs without errors on clean Odoo 19 CE |
| **1.5.2** Render test | Gantt view renders on a test model with date fields |
| **1.5.3** Interaction test | Drag-drop, resize, create pill, popover all functional |
| **1.5.4** Dependency test | Connector creation, cycle detection, cascading reschedule |

---

## Phase 2: ggg_rental (Application)

Full rental management application built on top of `ggg_gantt`.

### 2.1 Core Models

| Task | Description | Source Reference | Est. Lines |
|------|-------------|-----------------|------------|
| **2.1.1** `sale.temporal.recurrence` | Duration units (hour/day/week/month/year), overnight mode with pickup/return times | `sale_order_recurrence.py` | ~80 |
| **2.1.2** `product.pricing` | Pricing rules engine - recurrence-based pricing, PERIOD_RATIO conversion, ceiling rounding, best-price selection | `product_pricing.py` | ~250 |
| **2.1.3** `product.template` ext. | `rent_ok` flag, `product_pricing_ids`, `qty_in_rent`, `display_price`, `_get_best_pricing_rule()`, late fee fields | `product_template.py` | ~200 |
| **2.1.4** `product.product` ext. | `qty_in_rent` computed, `_compute_delay_price()`, variant-level pricing delegation | `product_product.py` | ~80 |
| **2.1.5** `product.pricelist` ext. | `_compute_price_rule()` override for rental pricing, `_enable_rental_price()` guard | `product_pricelist.py` | ~100 |
| **2.1.6** `sale.order` ext. | Rental dates, duration, `rental_status` state machine (draft/pickup/return/returned), `is_late`, pickup/return actions | `sale_order.py` | ~300 |
| **2.1.7** `sale.order.line` ext. | `is_rental`, `qty_returned`, `reservation_begin`, `rental_color`, `web_gantt_write()`, `_generate_delay_line()` | `sale_order_line.py` | ~350 |
| **2.1.8** `res.company` ext. | `extra_hour`, `extra_day`, `min_extra_hour`, `extra_product` (delay cost service) | `res_company.py` | ~30 |
| **2.1.9** `res.config.settings` ext. | Expose company fields + `ir.default` for product late fee defaults | `res_config_settings.py` | ~50 |

### 2.2 Wizard

| Task | Description | Source Reference | Est. Lines |
|------|-------------|-----------------|------------|
| **2.2.1** `rental.order.wizard` | Pickup/return wizard - loads eligible lines, validates quantities, applies changes, generates delay lines for late returns | `rental_processing.py` | ~200 |

### 2.3 Views & UI

| Task | Description | Source Reference |
|------|-------------|-----------------|
| **2.3.1** Product template views | Rental toggle, pricing rules tab, reservations section, tree/kanban price display | `product_template_views.xml` |
| **2.3.2** Product product views | In-rental stat button, Gantt link | `product_product_views.xml` |
| **2.3.3** Product pricing views | Pricing rules CRUD form/tree | `product_pricing_views.xml` |
| **2.3.4** Pricelist views | Rental pricing tab on pricelist form | `product_pricelist_views.xml` |
| **2.3.5** Sale order views | Rental period daterange, duration display, status badges, pickup/return buttons | `sale_order_views.xml` |
| **2.3.6** Sale order line views | Gantt schedule view (grouped by product, colored by status, drag-to-reschedule) | `sale_order_line_views.xml` |
| **2.3.7** Recurrence views | Manage rental periods (duration + unit CRUD) | `sale_temporal_recurrence_views.xml` |
| **2.3.8** Settings views | Delay costs, grace period, delay product configuration | `res_config_settings_views.xml` |
| **2.3.9** Menus | App menu: Orders, Schedule, Products, Reporting, Configuration | `sale_renting_menus.xml` |
| **2.3.10** Wizard views | Pickup/return dialog with quantity editors | `rental_processing_views.xml` |

### 2.4 Controllers

| Task | Description | Source Reference |
|------|-------------|-----------------|
| **2.4.1** Product configurator | Extends product configurator with rental dates and duration display | `product_configurator.py` |
| **2.4.2** Combo configurator | Extends combo configurator for rental combo products | `combo_configurator.py` |
| **2.4.3** Utils | Shared controller utilities | `utils.py` |

### 2.5 Reports

| Task | Description | Source Reference |
|------|-------------|-----------------|
| **2.5.1** Rental report | SQL view expanding rentals to daily records (qty, revenue per day) | `rental_report_views.xml` |
| **2.5.2** Order report templates | Rental-specific PDF/HTML order report | `rental_order_report_templates.xml` |

### 2.6 JavaScript

| Task | Description | Source Reference |
|------|-------------|-----------------|
| **2.6.1** Sale product field patch | Inject rental dates into product field RPC for pricing display | `sale_product_field.js` |
| **2.6.2** Schedule Gantt extensions | Override Gantt model/renderer for rental-specific behavior (web_gantt_write, popover) | `schedule_gantt_*.js` |
| **2.6.3** Configurator dialogs | Rental-aware product/combo configurator dialogs | `*_configurator_dialog.js` |

### 2.7 Data & Security

| Task | Description | Source Reference |
|------|-------------|-----------------|
| **2.7.1** Default recurrences | Seed data: Hourly, 3H, Daily, Nightly, Weekly, 2W, Monthly, Quarterly, Yearly, 3Y, 5Y | `rental_data.xml` |
| **2.7.2** Demo data | Sample rental products and orders | `rental_demo.xml` |
| **2.7.3** Access rights | Model ACLs for wizard, pricing, recurrence (user/salesman/manager) | `ir.model.access.csv` |
| **2.7.4** Record rules | Multi-company rules, rental-specific filters | `ir_rules.xml` |

### 2.8 Module Scaffolding

| Task | Description |
|------|-------------|
| **2.8.1** `__manifest__.py` | Module metadata, depends=['sale', 'ggg_gantt'], LGPL-3 license, asset registration, pre_init_hook |
| **2.8.2** `__init__.py` files | Model/controller/wizard imports |
| **2.8.3** Static assets | App icon, product images |

### 2.9 Verification

| Task | Description |
|------|-------------|
| **2.9.1** Install test | Module installs on Odoo 19 CE with ggg_gantt |
| **2.9.2** Product setup flow | Create rentable product with pricing rules |
| **2.9.3** Order flow | Create rental order, confirm, verify pricing calculation |
| **2.9.4** Pickup flow | Execute pickup wizard, verify qty_delivered updates |
| **2.9.5** Return flow | Execute return wizard, verify late fee generation |
| **2.9.6** Schedule test | Gantt view renders rentals, drag-to-reschedule recalculates prices |
| **2.9.7** Pricing test | Verify best-price selection across multiple pricing rules and durations |

---

## Phase 3: Polish & Hardening *(optional)*

| Task | Description |
|------|-------------|
| **3.1** Translations | i18n support (`.pot` file generation) |
| **3.2** Dark mode | Gantt dark mode SCSS |
| **3.3** Tour | Guided walkthrough for new users |
| **3.4** Unit tests | Python test suite for pricing engine, status machine, late fees |
| **3.5** JS tests | Frontend tests for Gantt interactions |
| **3.6** Performance | Large dataset testing (1000+ rental lines in Gantt) |
| **3.7** Documentation | User guide, developer notes |

---

## Architecture Reference

### Module Dependency Graph

```
┌─────────┐     ┌────────────┐
│   web   │     │    sale    │
│  (CE)   │     │   (CE)    │
└────┬────┘     └─────┬──────┘
     │                │
     ▼                │
┌────────────┐        │
│ ggg_gantt  │        │
│  (new CE)  │        │
└────┬───────┘        │
     │                │
     ▼                ▼
┌────────────────────────┐
│      ggg_rental        │
│       (new CE)         │
└────────────────────────┘
```

### Rental Status Machine

```
                  confirm
  draft ──────────────────▶ pickup (awaiting pickup)
    │                          │
    │ cancel                   │ pickup wizard
    ▼                          ▼
  cancel                  return (awaiting return)
                               │
                               │ return wizard
                               ▼
                           returned
                               │
                               │ if late:
                               ▼
                        delay line created
```

### Pricing Algorithm

```
Input: product, start_date, end_date, pricelist

For each applicable pricing rule:
  ┌──────────────────────────────────────────────────┐
  │  duration_hours = (end_date - start_date).hours  │
  │  rule_hours = rule.duration * PERIOD_RATIO[unit] │
  │  periods = ceil(duration_hours / rule_hours)      │
  │  total = rule.price * periods                     │
  └──────────────────────────────────────────────────┘

Return: rule with minimum total
```

### Gantt Renderer Architecture

```
GanttController
├── Layout + SearchBar + CogMenu
└── GanttRenderer (CSS Grid)
    ├── GanttRendererControls (nav + scale selector)
    ├── Header row (group headers + column headers)
    ├── Row headers (sticky, with progress bars)
    ├── Cell grid (scrollable, virtual)
    │   ├── Pills (grid-positioned, draggable, resizable)
    │   ├── Connectors (SVG Bezier curves)
    │   └── Selection ghosts (multi-create)
    ├── GanttPopover (on pill click)
    ├── GanttTimeDisplayBadge (during drag)
    └── Total row (consolidation)
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module prefix | `ggg_` | Avoids namespace collision with Odoo EE modules |
| License | LGPL-3 | Community compatible, allows proprietary use |
| Gantt as separate module | Yes | Reusable for other apps (project, planning, etc.) |
| Dark mode | Deferred to Phase 3 | Nice-to-have, not blocking |
| Tests | Phase 3 | Get functional first, harden later |
| Translations | Phase 3 | English-only for initial release |
| Build order | Gantt first | Hard dependency - rental can't work without it |

---

## Estimated Scope

| Component | Python | JS | XML/SCSS | Total |
|-----------|--------|-----|----------|-------|
| ggg_gantt | ~770L | ~7000L | ~32 files | ~8500L |
| ggg_rental | ~1640L | ~500L | ~15 files | ~2800L |
| **Total** | **~2410L** | **~7500L** | **~47 files** | **~11300L** |

---

## Getting Started

1. Start with **Phase 1.4** (ggg_gantt scaffolding)
2. Then **Phase 1.1** (Python backend)
3. Then **Phase 1.2** (JS frontend - biggest effort)
4. Verify with **Phase 1.5**
5. Move to **Phase 2** (ggg_rental)
