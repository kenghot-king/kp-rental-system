## ADDED Requirements

### Requirement: Return wizard offers three conditions
The return wizard line SHALL offer three condition choices: Good, Damaged, and Inspect.

#### Scenario: Good condition selected
- **WHEN** staff selects condition = Good for a return line
- **THEN** the stock move routes from Rental Location to Warehouse Stock (lot_stock_id)

#### Scenario: Damaged condition selected
- **WHEN** staff selects condition = Damaged for a return line
- **THEN** the stock move routes from Rental Location to the company's Damage Location

#### Scenario: Inspect condition selected
- **WHEN** staff selects condition = Inspect for a return line
- **THEN** the stock move routes from Rental Location to the company's Inspection Location

### Requirement: Fee and reason fields shown for Damaged and Inspect
The return wizard SHALL display damage fee and reason fields when condition is Damaged or Inspect. These fields SHALL be hidden when condition is Good.

#### Scenario: Damaged — fee and reason visible
- **WHEN** condition = Damaged
- **THEN** damage fee and damage reason fields are visible on the wizard line

#### Scenario: Inspect — fee and reason visible
- **WHEN** condition = Inspect
- **THEN** damage fee and damage reason fields are visible on the wizard line

#### Scenario: Good — fee and reason hidden
- **WHEN** condition = Good
- **THEN** damage fee and damage reason fields are hidden on the wizard line

### Requirement: Damage fee charged immediately for Damaged and Inspect
When condition is Damaged or Inspect and a fee greater than 0 is entered, the system SHALL create a damage fee SO line and a `rental.damage.log` record at the time the return is applied. Fee can be 0 (no line created).

#### Scenario: Fee > 0 on Damaged condition
- **WHEN** condition = Damaged and damage_fee > 0
- **THEN** a damage fee SO line is added to the sale order and a damage log entry is created

#### Scenario: Fee > 0 on Inspect condition
- **WHEN** condition = Inspect and damage_fee > 0
- **THEN** a damage fee SO line is added to the sale order and a damage log entry is created

#### Scenario: Fee = 0 on Inspect condition
- **WHEN** condition = Inspect and damage_fee = 0
- **THEN** no damage fee SO line is created and no damage log entry is created

### Requirement: UserError when required location is not configured
The system SHALL raise a UserError when the condition requires a location (Damaged or Inspect) that is not configured on the company.

#### Scenario: Damage Location missing
- **WHEN** condition = Damaged and company.damage_loc_id is not set
- **THEN** a UserError is raised with a message directing staff to configure the Damage Location in Settings

#### Scenario: Inspection Location missing
- **WHEN** condition = Inspect and company.inspection_loc_id is not set
- **THEN** a UserError is raised with a message directing staff to configure the Inspection Location in Settings

### Requirement: Order status unaffected by condition
The rental order SHALL complete normally (reaching `returned` state) regardless of which condition items are returned with. No new order states are introduced.

#### Scenario: All items returned with Inspect condition
- **WHEN** all rental line quantities are returned (qty_returned = qty_delivered) with condition = Inspect
- **THEN** the rental order transitions to `returned` state as normal
