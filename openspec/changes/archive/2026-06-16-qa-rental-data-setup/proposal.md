## Why

QA testers cannot easily simulate time-dependent rental states (Late Pickup, Late Return) without waiting for real time to pass, making it slow and inconsistent to test late-notification flows and related business logic. A dedicated QA tool lets testers manufacture any rental state instantly in a controlled, trackable, and reversible way.

## What Changes

- New `qa.scenario` model: permanent record for a test scenario applied to one or more rental orders
- New `qa.scenario.log` model: per-order audit trail of every date mutation with revert support
- New `group_qa_tester` security group controlling access to all QA features
- New **QA** section in the Rental sidebar menu (Scenarios + Logs submenus)
- Scenario types supported at launch: **Late Pickup**, **Late Return**
- Safety checks prevent mutation of orders in wrong rental status, already invoiced, or already late
- One-click revert per scenario restores all mutated orders to their original dates

## Capabilities

### New Capabilities

- `qa-scenario`: Create, apply, and revert QA test scenarios that manipulate rental order dates to simulate time-dependent states (Late Pickup, Late Return)
- `qa-scenario-log`: Per-order immutable audit log of every field mutation made by a QA scenario, with revert tracking

### Modified Capabilities

<!-- none -->

## Impact

- **New models**: `qa.scenario`, `qa.scenario.log`
- **New security group**: `ggg_rental.group_qa_tester`
- **Menu**: new QA section added to `rental_menu_root` in `sale_renting_menus.xml`
- **Fields mutated**: `sale.order.rental_start_date`, `sale.order.rental_return_date` (triggers recompute of `next_action_date`, `rental_status`, `is_late`)
- **No schema changes** to existing models — read-only access to `sale.order` fields
