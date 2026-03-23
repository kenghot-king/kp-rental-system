## ADDED Requirements

### Requirement: Rental location per company
The system SHALL create a dedicated internal stock location called "Rental" for each company. This location SHALL be a child of the Customers location but with `usage = 'internal'` so that rented products remain in inventory valuation. The location SHALL be stored on `res.company.rental_loc_id`.

#### Scenario: First rental module installation
- **WHEN** ggg_rental is installed on a database with the stock module
- **THEN** a "Rental" internal location is created for each company and linked via `rental_loc_id`

#### Scenario: New company created after installation
- **WHEN** a new company is created
- **THEN** a "Rental" internal location is automatically created for that company

### Requirement: Stock moves on pickup
The system SHALL create stock moves from warehouse stock location to the company's rental location when rental products are picked up (qty_delivered increases). The stock moves SHALL be immediately confirmed and done. The moved quantity SHALL equal the increase in qty_delivered.

#### Scenario: Full pickup of rental order
- **WHEN** a rental order line has qty 2 and the pickup wizard sets qty_delivered from 0 to 2
- **THEN** a stock move of qty 2 is created from Warehouse Stock → Rental Location and marked as done
- **THEN** the product's On Hand in Warehouse Stock decreases by 2
- **THEN** the product's On Hand in Rental Location increases by 2

#### Scenario: Partial pickup
- **WHEN** a rental order line has qty 3 and the pickup wizard sets qty_delivered from 0 to 2
- **THEN** a stock move of qty 2 is created (not 3)

#### Scenario: Second partial pickup
- **WHEN** a rental order line already has qty_delivered = 2 and pickup wizard adds 1 more
- **THEN** a new stock move of qty 1 is created from Warehouse Stock → Rental Location

### Requirement: Stock moves on return
The system SHALL create stock moves from the company's rental location back to warehouse stock location when rental products are returned (qty_returned increases). The stock moves SHALL be immediately confirmed and done.

#### Scenario: Full return of rental order
- **WHEN** a rental order line has qty_delivered = 2 and the return wizard sets qty_returned from 0 to 2
- **THEN** a stock move of qty 2 is created from Rental Location → Warehouse Stock and marked as done
- **THEN** the product's On Hand in Warehouse Stock increases by 2

#### Scenario: Partial return
- **WHEN** a rental order line has qty_delivered = 3 and the return wizard returns 1
- **THEN** a stock move of qty 1 is created from Rental Location → Warehouse Stock

### Requirement: Rental lines skip normal sale_stock procurement
The system SHALL prevent rental order lines from creating standard delivery pickings on SO confirmation. Only the manual stock moves from pickup/return wizards SHALL affect inventory for rental lines.

#### Scenario: Confirming a rental order
- **WHEN** a rental order with is_rental lines is confirmed
- **THEN** no outgoing delivery picking is created for the rental lines
- **THEN** non-rental lines on the same order (if any) still create normal delivery pickings

### Requirement: Storable products only
Stock moves SHALL only be created for storable (consu) products. Service products and other non-storable types SHALL be skipped during stock move creation.

#### Scenario: Service rental product
- **WHEN** a rental order line for a service-type product (e.g., Meeting Room) is picked up
- **THEN** qty_delivered is updated but no stock move is created

#### Scenario: Storable rental product
- **WHEN** a rental order line for a storable product (e.g., Power Bank) is picked up
- **THEN** qty_delivered is updated AND a stock move is created

### Requirement: Undo pickup/return stock moves
The system SHALL handle decreases in qty_delivered or qty_returned by reversing the corresponding stock moves (reducing move line quantities on previously created moves).

#### Scenario: Pickup quantity decreased
- **WHEN** qty_delivered on a rental line is decreased from 3 to 2
- **THEN** the previously created pickup stock move quantities are reduced by 1
- **THEN** 1 unit moves back from Rental Location to Warehouse Stock
