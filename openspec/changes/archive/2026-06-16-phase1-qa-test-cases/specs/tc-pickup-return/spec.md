## ADDED Requirements

### Requirement: Pickup wizard — bulk products
The system SHALL allow picking up non-serial-tracked products via the pickup wizard.

#### Scenario: TC-PK-001 Full pickup of bulk product
- **WHEN** confirmed order has 5 units of a non-tracked product, user opens pickup wizard and confirms qty_delivered=5
- **THEN** qty_delivered=5, delivery move validated, rental_status changes to "return"

#### Scenario: TC-PK-002 Partial pickup of bulk product
- **WHEN** confirmed order has 5 units, user picks up 3 via wizard
- **THEN** qty_delivered=3, rental_status remains "pickup", has_pickable_lines=True

#### Scenario: TC-PK-003 Pickup more than reserved auto-increases reserved
- **WHEN** order has 3 reserved, user enters qty_delivered=5 in wizard
- **THEN** product_uom_qty auto-increases to 5, qty_delivered=5

### Requirement: Pickup wizard — serial-tracked products
The system SHALL allow selecting specific serial numbers during pickup.

#### Scenario: TC-PK-004 Select serials from available stock
- **WHEN** order has serial-tracked product with 3 reserved, user opens pickup wizard
- **THEN** pickeable_lot_ids shows available serials in warehouse stock

#### Scenario: TC-PK-005 Pick specific serials
- **WHEN** user selects 2 serials from pickeable_lot_ids
- **THEN** qty_delivered auto-computes to 2, pickedup_lot_ids contains selected serials

#### Scenario: TC-PK-006 Serials assigned to stock move
- **WHEN** pickup wizard is applied with selected serials
- **THEN** delivery move lines have correct lot_id assignments, move is validated

### Requirement: Return wizard — bulk products
The system SHALL allow returning non-serial-tracked products via the return wizard.

#### Scenario: TC-RT-001 Full return of bulk product
- **WHEN** order has 5 picked-up units, user opens return wizard and confirms qty_returned=5
- **THEN** qty_returned=5, return stock move created and validated, rental_status="returned"

#### Scenario: TC-RT-002 Partial return of bulk product
- **WHEN** order has 5 picked-up units, user returns 2
- **THEN** qty_returned=2, rental_status remains "return"

#### Scenario: TC-RT-003 Cannot return more than picked up
- **WHEN** order has 3 picked-up units, user tries to return 5
- **THEN** system raises validation error

### Requirement: Return wizard — serial-tracked products
The system SHALL allow selecting specific serial numbers for return.

#### Scenario: TC-RT-004 Returnable serials shown
- **WHEN** order has 3 serials picked up (SN001, SN002, SN003), user opens return wizard
- **THEN** returnable_lot_ids shows SN001, SN002, SN003

#### Scenario: TC-RT-005 Return specific serials
- **WHEN** user selects SN001 and SN002 from returnable_lot_ids
- **THEN** qty_returned auto-computes to 2, returned_lot_ids contains SN001, SN002

#### Scenario: TC-RT-006 Second return shows remaining serials only
- **WHEN** SN001 and SN002 already returned, user opens return wizard again
- **THEN** returnable_lot_ids shows only SN003

#### Scenario: TC-RT-007 Return serial assigned to return stock move
- **WHEN** return wizard applied with selected serials
- **THEN** return move lines have correct lot_id, move validated, items back in warehouse stock

### Requirement: Wizard chatter logging
The system SHALL post pickup/return details to the order chatter.

#### Scenario: TC-PK-007 Pickup logged in chatter
- **WHEN** pickup wizard is applied
- **THEN** order chatter shows message with product name, quantity picked, and serial numbers (if applicable)

#### Scenario: TC-RT-008 Return logged in chatter
- **WHEN** return wizard is applied
- **THEN** order chatter shows message with product name, quantity returned, condition, and serial numbers (if applicable)
