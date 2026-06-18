## ADDED Requirements

### Requirement: QA tester can create a scenario record
A `qa.scenario` record SHALL capture: name, scenario type (Late Pickup / Late Return), number of days late, and a many2many selection of rental orders to target. The record SHALL be accessible only to users in `group_qa_tester`.

#### Scenario: Create scenario
- **WHEN** a QA tester opens the QA > Scenarios menu and creates a new record
- **THEN** the form shows fields: Name, Scenario (selection), Days Late (integer ≥ 1), Orders (many2many to sale.order filtered by is_rental_order=True), and state=Draft

---

### Requirement: Apply scenario pushes dates into the past
When a QA tester applies a scenario, the system SHALL write the appropriate date field on each valid order to `now() - timedelta(days=N)`, causing `is_late` to become True on those orders.

#### Scenario: Apply Late Pickup
- **WHEN** scenario type is Late Pickup and an order has rental_status='pickup' and is_late=False
- **THEN** `rental_start_date` is set to `now() - days`, `is_late` becomes True, a log entry is created, and scenario state becomes 'applied'

#### Scenario: Apply Late Return
- **WHEN** scenario type is Late Return and an order has rental_status='return' and is_late=False
- **THEN** `rental_return_date` is set to `now() - days`, `is_late` becomes True, a log entry is created, and scenario state becomes 'applied'

#### Scenario: Apply shows warning for skipped orders
- **WHEN** some selected orders fail safety checks
- **THEN** the system raises a non-blocking warning listing each skipped order and its reason; valid orders are still mutated

---

### Requirement: Safety checks block invalid orders
The system SHALL skip (not error) any order that fails any of these checks, with a per-order reason:
1. `is_rental_order` is False
2. `state` is not `sale`
3. `rental_status` does not match the scenario type
4. `is_late` is already True
5. Order has a posted invoice with uninvoiced quantities

#### Scenario: Skip already-late order
- **WHEN** an order's `is_late` is already True at apply time
- **THEN** the order is skipped with reason "Already late"

#### Scenario: Skip wrong status
- **WHEN** a Late Pickup scenario targets an order with rental_status='return'
- **THEN** the order is skipped with reason "Wrong rental status"

#### Scenario: Skip invoiced order
- **WHEN** an order has a posted invoice with qty_to_invoice > 0
- **THEN** the order is skipped with reason "Has open invoice"

---

### Requirement: Revert restores original dates for all orders in a scenario
The system SHALL restore all mutated orders to their pre-apply dates in a single action. After revert, `is_late` SHALL become False (assuming dates are in the future) and scenario state becomes 'reverted'.

#### Scenario: Revert Late Pickup
- **WHEN** a QA tester clicks Revert on an applied Late Pickup scenario
- **THEN** `rental_start_date` is restored to the original value from the log, `is_late` becomes False, and all log entries are marked reverted

#### Scenario: Warn on revert if rental_status changed
- **WHEN** an order's `rental_status` has changed since the scenario was applied (e.g., order was actually picked up)
- **THEN** the revert still writes the original date but displays a warning listing the orders whose status changed

---

### Requirement: Scenario state machine
A scenario SHALL follow the state progression: `draft` → `applied` → `reverted`. An applied scenario cannot be applied again. A draft scenario cannot be reverted.

#### Scenario: Block re-apply
- **WHEN** a QA tester attempts to apply an already-applied scenario
- **THEN** the system raises a UserError: "Scenario already applied"

#### Scenario: Block revert of draft
- **WHEN** a QA tester attempts to revert a draft scenario
- **THEN** the system raises a UserError: "Scenario has not been applied"
