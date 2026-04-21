## 1. JS Field Widget

- [x] 1.1 Create `addons/ggg_rental/static/src/js/completion_badge_field/completion_badge_field.js` — Owl component reading `rental_completion` and `rental_completion_detail`, using `usePopover()` for click-triggered detail display
- [x] 1.2 Create `addons/ggg_rental/static/src/js/completion_badge_field/completion_badge_field.xml` — Owl template: clickable `<span>` badge with Bootstrap classes, role="button", tabindex, keydown handler
- [x] 1.3 Create `addons/ggg_rental/static/src/js/completion_badge_field/completion_badge_popover.xml` — Popover body template rendering the detail text with `white-space: pre-line`
- [x] 1.4 Register the widget in the fields registry: `registry.category("fields").add("completion_badge", { component: CompletionBadgeField, supportedTypes: ["selection"], fieldDependencies: [{ name: "rental_completion_detail", type: "char" }] })`
- [x] 1.5 Create `addons/ggg_rental/static/src/js/completion_badge_field/completion_badge_field.scss` — minor styles (cursor: pointer, popover body spacing)

## 2. View Updates

- [x] 2.1 Form view: change `widget="badge"` → `widget="completion_badge"` on `rental_completion` field; remove `title="rental_completion_detail"`; remove the separate `<field name="rental_completion_detail" invisible="1"/>` declaration (widget declares it as dependency)
- [x] 2.2 List view: same widget swap; remove `<field name="rental_completion_detail" column_invisible="True"/>`
- [x] 2.3 Kanban view: remove the manual `<span>` badges with `t-att-title`; replace with `<field name="rental_completion" widget="completion_badge"/>`

## 3. Assets

- [x] 3.1 Verify `web.assets_backend` glob `ggg_rental/static/src/js/**/*` picks up new JS/XML/SCSS — no manifest change needed

## 4. Verification

- [x] 4.1 Test form view: click Incomplete badge → popover opens with 3 lines; click again or outside → closes
- [x] 4.2 Test list view: click Incomplete badge in a row → popover opens; click outside → closes
- [x] 4.3 Test kanban view: click badge on a card → popover opens correctly positioned
- [x] 4.4 Test Complete badge: click → popover shows confirmation message
- [x] 4.5 Test keyboard: Tab to focus badge, press Enter → popover opens; Escape → closes
- [x] 4.6 Test search/filter by completion still works (no regression)
