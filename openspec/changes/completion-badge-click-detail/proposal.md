## Why

The `rental-completion-status` change introduced an "Incomplete" badge with a hover tooltip showing the detail breakdown (returned x/y, paid x/y, deposit refunded amt/amt). Hover tooltips are inconsistent: they don't work reliably on touch devices, disappear quickly, and users expect status chips with drill-down information to be clickable. Staff need a reliable, accessible way to see completion detail without fiddling with hover timing.

## What Changes

- Replace the native `title` hover tooltip on the completion badge with a click-triggered popover.
- Clicking the "Incomplete" or "Complete" badge SHALL display the same detail breakdown (Returned, Paid, Deposit refunded) in a popover positioned next to the badge.
- The popover SHALL dismiss on outside click, Escape key, or a second click on the badge.
- Apply consistently in Form, List, and Kanban views.
- Badge remains searchable/filterable (no change to underlying stored field).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `rental-completion`: Interaction model for the detail breakdown changes from hover tooltip to click-triggered popover across all rental order views.

## Impact

- **Views**: `sale_order_views.xml` — remove `title` attribute, add custom widget reference on the badge field.
- **JS/Web assets**: New Owl component (or reuse existing popover widget) to render clickable badge with popover content. Registered as a field widget.
- **Manifest**: Add the JS component + optional SCSS to the `web.assets_backend` bundle.
- **No model changes**: `rental_completion` and `rental_completion_detail` fields remain unchanged.
