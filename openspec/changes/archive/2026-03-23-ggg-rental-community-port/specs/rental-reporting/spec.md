## ADDED Requirements

### Requirement: Rental report SQL view
The system SHALL provide a `sale.rental.report` model backed by a SQL view that expands each rental order line into daily records, with one row per product per day of the rental period.

#### Scenario: Daily expansion
- **WHEN** a rental line spans 5 days for product "Bike" with quantity 3
- **THEN** the report contains 5 rows, each with quantity=3 and daily revenue = total_price / 5

### Requirement: Rental report measures
The system SHALL expose the following measures in the report: `quantity` (daily ordered qty), `qty_delivered` (daily picked-up qty), `qty_returned` (daily returned qty), `price` (daily revenue = line subtotal / duration_days).

#### Scenario: Report measures available
- **WHEN** opening the Rental Analysis report
- **THEN** pivot and graph views can aggregate by quantity, qty_delivered, qty_returned, and price

### Requirement: Rental report views
The system SHALL provide graph (line chart by date), pivot (rows by date), and list views for the rental report, accessible from the Rental app's Reporting menu.

#### Scenario: Graph view default
- **WHEN** opening Reporting > Rental Analysis
- **THEN** a line chart displays rental quantity over time by default

#### Scenario: Pivot analysis
- **WHEN** switching to pivot view
- **THEN** the user can analyze rental data by product, date, customer, and salesperson dimensions

### Requirement: Rental order report template
The system SHALL provide a PDF/HTML report template for rental orders that includes rental-specific information (rental period, pickup/return dates).

#### Scenario: Print rental order
- **WHEN** printing a rental order
- **THEN** the report shows rental start date, return date, and rental-specific line details
