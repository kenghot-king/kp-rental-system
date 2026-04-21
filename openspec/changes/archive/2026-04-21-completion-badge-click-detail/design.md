## Context

The `rental-completion-status` change added a `rental_completion` selection field and `rental_completion_detail` char field on `sale.order`. The detail currently renders via native HTML `title` attributes (form/list) and `t-att-title` (kanban) to produce browser tooltips on hover.

Hover tooltips have known problems: they don't work on touch devices, are hard to read (dismiss quickly, no rich formatting), and users commonly expect status chips with drill-down to be clickable. This change replaces hover with a click-triggered popover.

Odoo 19's `@web/core/popover/popover_hook` already provides `usePopover()` for rendering arbitrary Owl components as popovers with outside-click and Escape dismissal built in. The popover service handles positioning and stacking.

## Goals / Non-Goals

**Goals:**
- Click the completion badge → popover opens with the detail breakdown.
- Click outside / press Escape / click the badge again → popover closes.
- Works identically in Form, List, and Kanban views.
- No change to stored model data or search/filter behavior.

**Non-Goals:**
- Adding icons, actions, or links inside the popover (plain text only for now).
- Replacing existing hover tooltips elsewhere in the app.
- Making the popover editable or interactive beyond display.
- Mobile bottom-sheet variant (out of scope; usePopover supports it via `useBottomSheet` if needed later).

## Decisions

### 1. Custom Owl field widget registered as `completion_badge`

**Choice**: Create a new Owl component `CompletionBadgeField` that renders as a clickable badge and uses `usePopover()` to open a popover with the detail text.

**Why**: Clean separation of concerns, reusable across views, uses Odoo's built-in popover service (no custom dismissal logic needed). Registered via `registry.category("fields").add("completion_badge", { component: CompletionBadgeField, supportedTypes: ["selection"] })`.

**Alternative considered**: Inline `<button>` + wizard/dialog. Rejected because a dialog is heavier than needed for a tooltip-style reveal.

**Alternative considered**: Patch the existing `badge` widget. Rejected because a dedicated widget is cleaner and avoids affecting other badges in the app.

### 2. Popover content is a simple component reading the detail string

**Choice**: The popover renders the `rental_completion_detail` value as a `<pre>`-like block (white-space: pre-line) so the `\n` separators from the server produce visible line breaks.

**Why**: The detail is already pre-formatted on the server (`'\n'.join(detail_parts)`). Rendering as pre-line preserves that formatting with zero additional logic.

### 3. Field widget reads both `rental_completion` and `rental_completion_detail` from record

**Choice**: The widget is bound to `rental_completion` (selection) but accesses `record.data.rental_completion_detail` for the popover body. Declare the detail field as a dependency via `fieldDependencies`.

**Why**: Odoo's field widget API supports declaring extra field dependencies so the record loads them. Keeps view XML clean — only `<field name="rental_completion" widget="completion_badge"/>` is needed.

### 4. Styling: reuse existing badge decorations

**Choice**: Apply the same `text-bg-success` / `text-bg-danger` Bootstrap badge classes the current implementation uses, keyed off the field value. No new SCSS file required beyond a tiny stylesheet for the clickable cursor and popover body formatting.

**Why**: Visual consistency with the rest of Odoo's badges. Minimal new CSS surface.

### 5. View updates: swap widget reference, drop title attributes

**Choice**:
- Form view: `widget="badge"` → `widget="completion_badge"`; drop `title="rental_completion_detail"`.
- List view: same.
- Kanban view: replace the `<span class="badge ... t-att-title=...">` markup with the field widget reference `<field name="rental_completion" widget="completion_badge"/>`.

**Why**: Single widget handles all three views identically. Kanban rendering supports field widgets.

**Alternative considered**: Keep hover in list view, click in form/kanban. Rejected — inconsistent UX.

## Risks / Trade-offs

- **[Kanban list tile complexity]** → Field widgets in kanban can behave differently from form due to limited interaction context. Mitigation: verify the popover opens correctly over the kanban card; if issues arise, a simpler kanban-specific variant can be used as fallback.

- **[Popover position on list view edge cases]** → When a row is near the viewport edge, the popover might overlap controls. Mitigation: Odoo's popover service handles repositioning automatically.

- **[Empty detail for complete status]** → Currently `rental_completion_detail` is `False` when status is `complete`. Clicking a "Complete" badge should either (a) not open a popover, or (b) show a confirmation like "All items returned, all invoices paid, deposit fully refunded". Decision: show a short confirmation message. The widget generates the confirmation text client-side when detail is empty, so no server change needed.

- **[Accessibility]** → A clickable badge needs proper `role="button"` and keyboard (Enter/Space) support. Mitigation: the Owl component will add `tabindex="0"`, `role="button"`, and handle keydown events.
