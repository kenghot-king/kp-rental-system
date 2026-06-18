## ADDED Requirements

### Requirement: Rental analysis report
The system SHALL provide a daily rental analysis report with pivot, graph, and list views.

#### Scenario: TC-RP-001 Report shows daily breakdown
- **WHEN** order has 3-day rental for 2 units at 600 THB total
- **THEN** report shows 3 rows (one per day), each with quantity=0.67, price=200

#### Scenario: TC-RP-002 Group by product
- **WHEN** user groups report by product in pivot view
- **THEN** products are grouped with summed quantities and prices

#### Scenario: TC-RP-003 Group by salesperson
- **WHEN** user groups by salesperson
- **THEN** each salesperson shows their rental totals

#### Scenario: TC-RP-004 Filter by date range
- **WHEN** user filters report to 2026-04-01 through 2026-04-30
- **THEN** only rental days within that range are shown

#### Scenario: TC-RP-005 Graph view displays correctly
- **WHEN** user switches to graph view
- **THEN** line chart shows rental revenue over time

### Requirement: Schedule (Gantt) view
The system SHALL provide a Gantt chart of rental order lines showing rental periods.

#### Scenario: TC-RP-006 Gantt shows all active rentals
- **WHEN** user opens Schedule view
- **THEN** all confirmed rental order lines appear as bars from start_date to return_date

#### Scenario: TC-RP-007 Color coding by status
- **WHEN** viewing Gantt with orders in various statuses
- **THEN** bars are color-coded: blue=on-time pickup, red=late pickup, green=on-time return, orange=late return, gray=returned

#### Scenario: TC-RP-008 Drag to reschedule
- **WHEN** user drags a Gantt bar to new dates
- **THEN** rental dates update and prices recalculate

#### Scenario: TC-RP-009 Group by product
- **WHEN** user groups Gantt by product
- **THEN** each product row shows its rental order lines

### Requirement: Rental order list view
The system SHALL display rental orders with status badges and next action date.

#### Scenario: TC-RP-010 List view shows rental status badges
- **WHEN** user views rental order list
- **THEN** each order shows colored status badge (draft=info, pickup=success, return=warning)

#### Scenario: TC-RP-011 Next action date shown
- **WHEN** order has rental_status=pickup
- **THEN** next_action_date column shows rental_start_date with remaining days widget

### Requirement: Product catalog for rentals
The system SHALL show rental products with pricing and availability in the rental app.

#### Scenario: TC-RP-012 Product shows qty in rent
- **WHEN** 5 units of product are currently rented out
- **THEN** product form shows qty_in_rent=5

#### Scenario: TC-RP-013 Product shows display price
- **WHEN** product has pricing 100 THB/day
- **THEN** product list shows "100.00 THB / 1 Day"

### Requirement: User access control
The system SHALL enforce role-based access to rental features.

#### Scenario: TC-RP-014 Salesman can create orders
- **WHEN** user with Salesman group accesses rental orders
- **THEN** user can create, read, and edit rental orders

#### Scenario: TC-RP-015 Salesman cannot delete damage logs
- **WHEN** user with Salesman group tries to delete a rental.damage.log record
- **THEN** system denies the operation

#### Scenario: TC-RP-016 Manager can access reporting
- **WHEN** user with Manager group accesses Rental > Reporting
- **THEN** rental analysis report is accessible

#### Scenario: TC-RP-017 Settings restricted to system admin
- **WHEN** user without System admin group tries to access Rental > Configuration > Settings
- **THEN** settings page is not accessible
