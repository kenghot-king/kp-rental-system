## ADDED Requirements

### Requirement: Log entry records every field mutation
For each order mutated by a scenario apply, the system SHALL create a `qa.scenario.log` record capturing: scenario, order, field changed, original value, new value, applied by (user), applied at (datetime), and a reverted flag (default False).

#### Scenario: Log created on apply
- **WHEN** a scenario is applied and an order's date is mutated
- **THEN** a `qa.scenario.log` entry is created with `original_value` = the date before mutation, `new_value` = the mutated date, `reverted` = False

#### Scenario: Log is read-only
- **WHEN** a QA tester views the log
- **THEN** all fields are read-only; no editing is permitted

---

### Requirement: Log entry is marked reverted after scenario revert
When a scenario is reverted, each corresponding log entry SHALL have `reverted` set to True.

#### Scenario: Reverted flag set
- **WHEN** a scenario revert completes
- **THEN** all `qa.scenario.log` records linked to that scenario have `reverted=True`

---

### Requirement: QA Logs menu shows all log entries
The system SHALL provide a QA > Logs list view accessible to `group_qa_tester` showing all log entries with: order name, scenario name, field changed, original value, new value, applied by, applied at, and reverted status.

#### Scenario: View logs
- **WHEN** a QA tester opens QA > Logs
- **THEN** all log entries are listed with the fields above; no create/edit/delete buttons are shown
