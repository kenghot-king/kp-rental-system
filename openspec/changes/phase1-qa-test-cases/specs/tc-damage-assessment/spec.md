## ADDED Requirements

### Requirement: Damage condition assessment during return
The system SHALL allow staff to mark items as good or damaged during return, with fee and reason fields for damaged items.

#### Scenario: TC-DA-001 Return item in good condition
- **WHEN** user returns item and sets condition=good
- **THEN** no damage fee line created, no damage log record, item returned normally

#### Scenario: TC-DA-002 Return item as damaged with fee
- **WHEN** user returns item, sets condition=damaged, damage_fee=500, damage_reason="Scratched surface"
- **THEN** damage fee SO line created with price=500, description includes "Scratched surface"

#### Scenario: TC-DA-003 Damage fields hidden when condition is good
- **WHEN** condition=good in return wizard
- **THEN** damage_fee and damage_reason fields are not visible

#### Scenario: TC-DA-004 Damage fields shown when condition is damaged
- **WHEN** user selects condition=damaged in return wizard
- **THEN** damage_fee and damage_reason fields become visible

#### Scenario: TC-DA-005 Damage fields hidden during pickup
- **WHEN** wizard is in pickup mode (status=pickup)
- **THEN** condition, damage_fee, damage_reason columns are not visible

### Requirement: Damage fee SO line creation
The system SHALL create a service SO line for damage fees using the configured damage product.

#### Scenario: TC-DA-006 Damage line uses configured damage product
- **WHEN** company.damage_product is set to "Damage Fee" service product and a damaged return occurs
- **THEN** damage SO line uses the configured damage product

#### Scenario: TC-DA-007 Damage product auto-created if not configured
- **WHEN** company.damage_product is not set and a damaged return occurs
- **THEN** system auto-creates a "Rental Damage Fee" service product with default_code="DAMAGE"

#### Scenario: TC-DA-008 Damage line not marked as rental
- **WHEN** damage fee line is created
- **THEN** line has is_rental=False (invoiced as regular service)

### Requirement: Damage log record creation
The system SHALL create a rental.damage.log record for each damage assessment.

#### Scenario: TC-DA-009 Damage log created for bulk product
- **WHEN** bulk product returned as damaged with fee=500
- **THEN** rental.damage.log created with: lot_id=False, damage_fee=500, reason, order_id, product_id, user_id=current user

#### Scenario: TC-DA-010 Damage log created per serial
- **WHEN** serial-tracked product with 3 serials returned as damaged, total fee=900
- **THEN** 3 rental.damage.log records created, each with fee=300 (900/3), each linked to its serial

#### Scenario: TC-DA-011 Damage fee split equally across serials
- **WHEN** 2 serials returned as damaged with total damage_fee=500
- **THEN** 2 damage SO lines created, each with price=250, 2 damage logs each with fee=250

### Requirement: Damage history on serial numbers
The system SHALL show damage history on the stock.lot form.

#### Scenario: TC-DA-012 Damage count on serial form
- **WHEN** serial SN001 has been damaged in 2 separate rental orders
- **THEN** stock.lot form shows damage_count=2, smart button "Damage History (2)"

#### Scenario: TC-DA-013 View damage logs from serial
- **WHEN** user clicks "Damage History" button on stock.lot form
- **THEN** list view shows all rental.damage.log records for that serial with dates, orders, fees, reasons

### Requirement: Damage product configuration
The system SHALL allow configuring the damage product in rental settings.

#### Scenario: TC-DA-014 Set damage product in settings
- **WHEN** admin sets damage_product to a service product in Rental > Configuration > Settings
- **THEN** subsequent damage assessments use that product for the damage SO line
