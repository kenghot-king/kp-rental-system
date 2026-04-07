## ADDED Requirements

### Requirement: Delivery move on order confirmation
The system SHALL create a stock move from warehouse to rental location when a rental order is confirmed.

#### Scenario: TC-ST-001 Delivery move created on confirm
- **WHEN** rental order is confirmed (action_confirm)
- **THEN** stock move created: source=WH/Stock, destination=company.rental_loc_id, product and qty matching SO line

#### Scenario: TC-ST-002 Rental location auto-created per company
- **WHEN** a new company is created
- **THEN** system auto-creates a "Rental" internal location under the Customers location

### Requirement: Pickup validates delivery move
The system SHALL mark the delivery stock move as done when items are picked up.

#### Scenario: TC-ST-003 Pickup validates delivery move
- **WHEN** pickup wizard is applied for all reserved items
- **THEN** delivery stock move state changes to "done"

#### Scenario: TC-ST-004 Serial numbers assigned to move lines
- **WHEN** serial-tracked product picked up with specific serials selected
- **THEN** stock move lines have correct lot_id for each serial

### Requirement: Return creates and validates return move
The system SHALL create a return stock move from rental location back to warehouse on return.

#### Scenario: TC-ST-005 Return move created and validated
- **WHEN** return wizard is applied
- **THEN** new stock move created: source=rental_loc_id, destination=WH/Stock, move is validated (done)

#### Scenario: TC-ST-006 Return serials assigned to return move
- **WHEN** serial-tracked products returned with specific serials
- **THEN** return move lines have correct lot_id for each returned serial

#### Scenario: TC-ST-007 Stock restored after return
- **WHEN** all items returned
- **THEN** product qty available in warehouse increases by returned quantity

### Requirement: Stock move visibility on order
The system SHALL show rental stock move count on the order form.

#### Scenario: TC-ST-008 Stock move count displayed
- **WHEN** order has 2 stock moves (1 delivery + 1 return)
- **THEN** order form shows "Stock Moves (2)" button

#### Scenario: TC-ST-009 View stock moves from order
- **WHEN** user clicks stock moves button on rental order
- **THEN** list view shows all delivery and return moves for this order

### Requirement: Qty in rent tracking
The system SHALL track how many units of a product are currently rented out.

#### Scenario: TC-ST-010 Qty in rent increases on pickup
- **WHEN** 3 units of product are picked up
- **THEN** product.qty_in_rent increases by 3

#### Scenario: TC-ST-011 Qty in rent decreases on return
- **WHEN** 2 of 3 rented units are returned
- **THEN** product.qty_in_rent decreases by 2 (1 still in rent)
