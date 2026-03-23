## Context

We are rewriting two Odoo 19 Enterprise modules (`web_gantt` and `sale_renting`) as Community-licensed addons (`ggg_gantt` and `ggg_rental`). The Enterprise source at `enterprise/` serves as architectural reference. The target is `addons/ggg_gantt/` and `addons/ggg_rental/`.

The project runs on Odoo 19 Community Edition. The Gantt view is a prerequisite — the rental module cannot function without it. Both modules are additive and do not modify existing Community behavior when not installed.

**Constraints:**
- Must not import or depend on any Enterprise module
- Must use LGPL-3 license
- Must follow Odoo 19 module conventions (OWL 2, asset bundles, `__manifest__.py`)
- Enterprise source is reference only — code must be rewritten, not copied

## Goals / Non-Goals

**Goals:**
- Fully functional Gantt view usable by any Odoo model (not just rental)
- Feature-complete rental application matching Enterprise capabilities (product setup, pricing, orders, pickup/return, late fees, schedule, reporting)
- Clean module boundaries: `ggg_gantt` is standalone, `ggg_rental` depends on it
- Production-ready for Odoo 19 CE deployments

**Non-Goals:**
- Dark mode support (deferred)
- Translations / i18n (English-only initially)
- Automated test suites (deferred to hardening phase)
- Guided tours
- Backwards compatibility with Enterprise data (no migration tooling)
- Mobile-specific optimizations

## Decisions

### D1: Two separate modules, not one monolith

**Choice:** Split into `ggg_gantt` (view infrastructure) and `ggg_rental` (application).

**Alternatives considered:**
- Single `ggg_rental` module with embedded Gantt → Limits reusability. Other apps (project, manufacturing) couldn't use the Gantt view.
- Three modules (gantt + pricing + rental) → Over-engineered for current scope. Pricing has no standalone use case.

**Rationale:** The Gantt view is a general-purpose UI component. Keeping it separate follows Odoo's own architecture and allows future reuse.

### D2: Module naming with `ggg_` prefix

**Choice:** Use `ggg_` prefix for all module technical names (`ggg_gantt`, `ggg_rental`).

**Rationale:** Avoids namespace collision with Odoo's own `web_gantt` and `sale_renting` if Enterprise modules are ever present in the addons path. Short, consistent prefix.

### D3: Gantt Python API — extend `base` model with mixin

**Choice:** Add Gantt methods directly to the `base` abstract model, making `get_gantt_data()` and `web_gantt_reschedule()` available on every model.

**Alternatives considered:**
- Dedicated `gantt.mixin` model that must be explicitly inherited → Requires every consuming model to add `_inherit = 'gantt.mixin'`. More explicit but breaks the seamless "any model can have a Gantt view" pattern.

**Rationale:** Matches Enterprise architecture. Any model with `date_start`/`date_stop` fields can instantly use a Gantt view without additional inheritance. The methods are no-ops on models that don't define date fields.

### D4: Gantt JS — full MVC with OWL 2 components

**Choice:** Implement `GanttController`, `GanttModel`, `GanttRenderer` as OWL 2 components, registered as view type `gantt` in Odoo's view registry.

**Architecture:**
```
gantt_view.js (registration)
├── gantt_arch_parser.js    → Parses <gantt> XML arch
├── gantt_model.js          → Fetches data via get_gantt_data() RPC
├── gantt_renderer.js       → CSS Grid layout + interactions
├── gantt_controller.js     → Lifecycle + dialogs + search
├── gantt_helpers.js        → Date math + grid utilities
├── gantt_connector.js      → SVG dependency lines
└── Sub-components:
    ├── gantt_popover.js
    ├── gantt_scale_selector.js
    ├── gantt_row_progress_bar.js
    ├── gantt_renderer_controls.js
    ├── gantt_time_display_badge.js
    ├── gantt_multi_selection_buttons.js
    └── gantt_popover_in_dialog.js
```

**Rationale:** Follows Odoo's standard view pattern (see list, kanban, calendar views). CSS Grid provides performant layout without third-party dependencies. Virtual scrolling handles large datasets.

### D5: Gantt renderer uses CSS Grid with virtual scrolling

**Choice:** CSS Grid for pill/row/column positioning. Virtual grid renders only visible rows and columns.

**Alternatives considered:**
- Canvas-based rendering → Better for very large datasets but loses DOM accessibility, harder to style, breaks Odoo's component model.
- Full DOM rendering (no virtualization) → Simpler but unusable with 500+ rows.

**Rationale:** CSS Grid is the sweet spot — performant, styleable, accessible, and compatible with OWL's DOM-based rendering. Virtual scrolling adds the scalability needed for production datasets.

### D6: Rental pricing — PERIOD_RATIO conversion with ceiling rounding

**Choice:** Convert all durations to hours using a fixed ratio table, then ceiling-round to the pricing rule's recurrence unit.

```python
PERIOD_RATIO = {
    'hour': 1, 'day': 24, 'week': 168,
    'month': 744, 'year': 8928
}
```

**Alternatives considered:**
- Calendar-accurate duration (using `relativedelta`) → More precise for months/years but inconsistent behavior (28 vs 31 day months). Harder to reason about pricing.
- Floor rounding → Undercharges customers for partial periods.

**Rationale:** Ceiling rounding is standard in the rental industry (you pay for the full period even if you use part of it). Fixed ratios are predictable and testable. Enterprise uses this same approach.

### D7: Rental status — computed field with SQL search

**Choice:** `rental_status` is a computed stored field on `sale.order` with a custom `_search` method using raw SQL for efficient filtering.

**Status values:** `draft` → `pickup` → `return` → `returned`

**Rationale:** Status depends on line-level quantities (qty_delivered, qty_returned) which change frequently. Stored computation + SQL search gives both read performance (indexed) and write correctness (auto-recomputed).

### D8: Late fees — auto-generated service line on return

**Choice:** When a late return is processed through the wizard, automatically create a new `sale.order.line` with a service product and calculated delay cost.

**Formula:** `fee = days × extra_daily + hours × extra_hourly` (after grace period).

**Alternatives considered:**
- Separate invoice for late fees → More complex, splits billing.
- Manual late fee entry → Error-prone, inconsistent.

**Rationale:** Adding to the existing SO keeps billing unified. The grace period (`min_extra_hour`, default 2 hours) prevents fees for minor delays. A dedicated service product (`extra_product`) makes the fee visible and configurable.

### D9: Gantt schedule — SOL-based with `web_gantt_write` override

**Choice:** The rental schedule Gantt view operates on `sale.order.line` records, grouped by product. Drag-and-drop calls a custom `web_gantt_write()` method that validates date changes and recalculates pricing.

**Validations:**
- Cannot change `start_date` after pickup (status = 'return' or 'returned')
- Cannot change `return_date` after return (status = 'returned')
- Price auto-recalculated on duration change

**Rationale:** SOL-level granularity allows per-product scheduling within a single order. The custom write method prevents invalid state transitions while keeping the Gantt drag-drop UX smooth.

### D10: Asset registration — backend lazy loading

**Choice:** Register Gantt JS/CSS in `web.assets_backend_lazy` (loaded on demand when a Gantt view is opened), not `web.assets_backend` (loaded on every page).

**Rationale:** ~7000 lines of JS shouldn't load on every backend page. Lazy loading keeps initial page load fast. Rental-specific JS goes in `web.assets_backend` since it patches the sale product field globally.

### D11: Pre-init hook for database columns

**Choice:** Use `pre_init_hook` in `ggg_rental` to create rental columns via raw SQL before ORM initialization.

**Columns:** `rental_start_date`, `rental_return_date`, `rental_status`, `next_action_date` on `sale_order`; `reservation_begin` on `sale_order_line`.

**Rationale:** Avoids slow Python-computed field initialization on large existing `sale_order` tables during module installation. Enterprise uses the same pattern.

## Risks / Trade-offs

**[Gantt renderer complexity] → Incremental development**
The renderer is ~3500 lines with drag/resize/connect/virtual-scroll interactions. Risk of bugs in edge cases. Mitigation: Build core rendering first, add interactions incrementally, test each interaction mode independently.

**[Enterprise API drift] → Pin to Odoo 19**
Enterprise may change internal APIs in future versions. Mitigation: Target Odoo 19 only. Document all `@web/*` import paths used. Version-pin in `__manifest__.py`.

**[Pricing edge cases] → Match Enterprise behavior**
Duration conversion with PERIOD_RATIO is approximate (month = 31 days). Edge cases around DST transitions, leap years. Mitigation: Use the same constants as Enterprise for consistency. Document known approximations.

**[No automated tests initially] → Manual verification checklist**
Deferring tests increases regression risk. Mitigation: Phase 1/2 verification tasks include manual test scenarios. Phase 3 adds automated tests before production deployment.

**[CSS Grid browser compatibility] → Modern browsers only**
CSS Grid with named lines and subgrid features require modern browsers. Mitigation: Odoo 19 already requires modern browsers. No IE11 support needed.

**[Large JS bundle] → Lazy loading**
~7500 lines of new JS. Mitigation: Gantt assets loaded lazily (D10). Tree-shaking via Odoo's asset pipeline handles dead code.
