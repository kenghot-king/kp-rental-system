## ADDED Requirements

### Requirement: Delivery picking created on SO confirmation
When a rental SO is confirmed, the system SHALL create a delivery picking from WH/Stock to the company's Rental Location for each rental line with a storable product. The picking SHALL reserve stock so that "Free to Use" decreases by the ordered quantity.

#### Scenario: Confirm rental SO with storable product
- **WHEN** a rental SO with 2x "Power Bank 10Kw" (storable, on hand = 5) is confirmed
- **THEN** a delivery picking is created (WH/Stock → Rental Location) with qty = 2
- **THEN** the picking is in "assigned" state with stock reserved
- **THEN** Free to Use = 3, On Hand = 5

#### Scenario: Confirm rental SO with service product
- **WHEN** a rental SO with a service-type rental product is confirmed
- **THEN** no delivery picking is created for that line

#### Scenario: Confirm rental SO with non-rental lines
- **WHEN** a rental SO also contains non-rental sale lines with storable products
- **THEN** non-rental lines create standard customer delivery pickings as usual
- **THEN** rental lines create pickings to the Rental Location

### Requirement: Full quantity pickup via wizard
When performing a rental pickup via the wizard, the system SHALL validate the existing delivery picking for the full reserved quantity. The pickup quantity field SHALL be readonly — partial pickup is not allowed.

#### Scenario: Pickup full quantity (untracked product)
- **WHEN** user opens the pickup wizard for a confirmed rental SO with qty = 3
- **THEN** qty_delivered is set to 3 and the field is readonly
- **THEN** validating the wizard validates the delivery picking
- **THEN** On Hand decreases by 3, stock is now in Rental Location

#### Scenario: Pickup serial-tracked product
- **WHEN** user opens the pickup wizard for a serial-tracked product with qty = 2
- **THEN** qty_delivered is set to 2 and readonly
- **THEN** user selects 2 serial numbers from available lots
- **THEN** validating the wizard assigns the selected lots to the picking's move lines and validates

#### Scenario: Pickup quantity is locked
- **WHEN** user opens the pickup wizard
- **THEN** the qty_delivered field is not editable
- **THEN** the quantity always equals the full reserved amount

### Requirement: Partial return via new picking
When performing a rental return via the wizard, the system SHALL create a new return picking (Rental Location → WH/Stock) and validate it immediately. Partial returns are allowed.

#### Scenario: Full return (untracked product)
- **WHEN** user returns all 3 units via the return wizard
- **THEN** a return picking is created (Rental Location → WH/Stock) with qty = 3
- **THEN** the picking is validated immediately
- **THEN** On Hand increases by 3

#### Scenario: Partial return (untracked product)
- **WHEN** user returns 2 of 3 picked-up units via the return wizard
- **THEN** a return picking is created with qty = 2 and validated
- **THEN** On Hand increases by 2
- **THEN** user can later return the remaining 1 unit

#### Scenario: Return serial-tracked product
- **WHEN** user returns specific serial numbers via the return wizard
- **THEN** a return picking is created with the selected lots assigned to move lines
- **THEN** the picking is validated and On Hand increases
