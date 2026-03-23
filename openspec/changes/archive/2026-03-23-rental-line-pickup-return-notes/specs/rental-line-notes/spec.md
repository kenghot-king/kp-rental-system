## ADDED Requirements

### Requirement: Pickup note on SO line for serial-tracked products
After a rental pickup of a serial-tracked product, the SO line `name` SHALL be updated to include a "Picked up:" line listing the serial numbers.

#### Scenario: Pickup serial-tracked product
- **WHEN** a pickup is performed for a serial-tracked product with lots SN001 and SN002
- **THEN** the SO line name is updated to append "\nPicked up: SN001, SN002"

### Requirement: Pickup note on SO line for non-tracked products
After a rental pickup of a non-tracked product, the SO line `name` SHALL be updated to include a "Picked up:" line showing the quantity.

#### Scenario: Pickup non-tracked product
- **WHEN** a pickup is performed for a non-tracked product with qty_delivered = 3
- **THEN** the SO line name is updated to append "\nPicked up: 3"

### Requirement: Return note on SO line for serial-tracked products
After a rental return of a serial-tracked product, the SO line `name` SHALL be updated to include a "Returned:" line listing the returned serial numbers.

#### Scenario: Full return serial-tracked product
- **WHEN** lots SN001 and SN002 were picked up and both are returned
- **THEN** the SO line name includes "\nPicked up: SN001, SN002\nReturned: SN001, SN002"

#### Scenario: Partial return serial-tracked product
- **WHEN** lots SN001 and SN002 were picked up and only SN001 is returned
- **THEN** the SO line name includes "\nPicked up: SN001, SN002\nReturned: SN001"

### Requirement: Return note on SO line for non-tracked products
After a rental return of a non-tracked product, the SO line `name` SHALL be updated to include a "Returned:" line showing the returned quantity.

#### Scenario: Partial return non-tracked product
- **WHEN** 3 units were picked up and 2 are returned
- **THEN** the SO line name includes "\nPicked up: 3\nReturned: 2"

### Requirement: Notes rebuild on each event
The pickup/return notes portion of the SO line name SHALL be rebuilt from current state on each pickup or return event, not appended incrementally.

#### Scenario: Notes reflect current state after multiple returns
- **WHEN** 3 units are picked up, then 1 is returned, then 1 more is returned
- **THEN** the SO line name shows "Picked up: 3\nReturned: 2" (not two separate "Returned:" lines)

### Requirement: Invoice inherits notes
Invoice lines created from SO lines with pickup/return notes SHALL include those notes in their description automatically via the existing name inheritance.

#### Scenario: Invoice after pickup
- **WHEN** an invoice is created after a pickup has occurred
- **THEN** the invoice line description includes the "Picked up:" note
