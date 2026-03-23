## ADDED Requirements

### Requirement: Rental order identification
The system SHALL add an `is_rental_order` boolean field to `sale.order` that is TRUE when the order is created in the rental app context or contains rented products. A related `has_rented_products` computed field SHALL be TRUE if any order line has `is_rental=True`.

#### Scenario: Order created in rental app
- **WHEN** a sale order is created with `context.in_rental_app=True`
- **THEN** `is_rental_order` is TRUE

#### Scenario: Rental product added to regular order
- **WHEN** a rent_ok product is added to a non-rental order
- **THEN** `has_rented_products` becomes TRUE

### Requirement: Rental date period
The system SHALL add `rental_start_date` and `rental_return_date` datetime fields to `sale.order`, with computed `duration_days` (integer) and `remaining_hours` (integer, ceiling-rounded).

#### Scenario: Duration calculation
- **WHEN** `rental_start_date=2024-10-01 10:00` and `rental_return_date=2024-10-04 14:00`
- **THEN** `duration_days=3` and `remaining_hours=4`

#### Scenario: Date coherence constraint
- **WHEN** `rental_start_date` is set after `rental_return_date`
- **THEN** the system raises a validation error

#### Scenario: Auto-set dates on first access
- **WHEN** a rental order is created without dates
- **THEN** `rental_start_date` defaults to now + 1 hour (top of hour) and `rental_return_date` defaults to start + 1 day

### Requirement: Rental status machine
The system SHALL compute a `rental_status` field on `sale.order` with values: `draft`, `pickup` (confirmed, awaiting pickup), `return` (picked up, awaiting return), `returned` (all items back), and `cancel`.

#### Scenario: Confirmed order with pickable lines
- **WHEN** a rental order is confirmed (state='sale') and has lines where `qty_delivered < product_uom_qty`
- **THEN** `rental_status` is `pickup`

#### Scenario: All items picked up
- **WHEN** all rental lines have `qty_delivered >= product_uom_qty` and some have `qty_returned < qty_delivered`
- **THEN** `rental_status` is `return`

#### Scenario: All items returned
- **WHEN** all rental lines have `qty_returned >= qty_delivered` and `qty_delivered >= product_uom_qty`
- **THEN** `rental_status` is `returned`

### Requirement: Late detection
The system SHALL compute `is_late` (boolean) on `sale.order` when `rental_status` is `pickup` or `return` and `next_action_date < now`. The `next_action_date` SHALL be `rental_start_date` for pickup status and `rental_return_date` for return status.

#### Scenario: Late pickup
- **WHEN** rental_status is `pickup` and `rental_start_date` has passed
- **THEN** `is_late` is TRUE

#### Scenario: Late return
- **WHEN** rental_status is `return` and `rental_return_date` has passed
- **THEN** `is_late` is TRUE

#### Scenario: Efficient late search
- **WHEN** filtering orders by `is_late=True`
- **THEN** the system uses a SQL-based search for efficient filtering on large datasets

### Requirement: Rental order line identification
The system SHALL add `is_rental` (boolean, stored) to `sale.order.line` that is TRUE when the product has `rent_ok=True` and the order is in rental context. Lines SHALL have `start_date` and `return_date` (related to SO dates), `qty_returned` (float, default 0), and `reservation_begin` (stored, = start_date when is_rental).

#### Scenario: Rental line created
- **WHEN** a rent_ok product is added to a rental order
- **THEN** `is_rental=True`, `start_date` and `return_date` link to the SO's rental dates

#### Scenario: Manual delivery method
- **WHEN** a line has `is_rental=True`
- **THEN** `qty_delivered_method` is `manual` (not stock-based)

### Requirement: Rental line status
The system SHALL compute `rental_status` on `sale.order.line` with values `pickup`, `return`, `returned` based on quantity comparisons, and `rental_color` (integer) for Gantt visualization.

#### Scenario: Line status colors
- **WHEN** a rental line has state=draft/sent → `rental_color=5` (purple)
- **WHEN** rental_status=pickup and on time → `rental_color=4` (blue)
- **WHEN** rental_status=pickup and late → `rental_color=3` (yellow)
- **WHEN** rental_status=return and on time → `rental_color=2` (orange)
- **WHEN** rental_status=return and late → `rental_color=6` (red)
- **WHEN** rental_status=returned → `rental_color=7` (green)

### Requirement: Update rental prices on duration change
The system SHALL provide an `action_update_rental_prices()` method on `sale.order` that recalculates all rental line prices based on the current rental period. A `show_update_duration` transient flag SHALL indicate when prices need recalculation.

#### Scenario: Date changed triggers price update
- **WHEN** a user changes `rental_return_date` on a confirmed order and clicks "Update Rental Prices"
- **THEN** all rental lines recalculate their unit price using the new duration and best pricing rule

### Requirement: Gantt schedule write validation
The system SHALL provide `web_gantt_write()` on `sale.order.line` that validates date changes based on rental status before writing, and recalculates prices if the duration changes.

#### Scenario: Cannot change start after pickup
- **WHEN** a Gantt drag attempts to change `start_date` on a line with `rental_status='return'`
- **THEN** the write is rejected with a notification

#### Scenario: Cannot change return after returned
- **WHEN** a Gantt drag attempts to change `return_date` on a line with `rental_status='returned'`
- **THEN** the write is rejected with a notification

#### Scenario: Valid date change recalculates price
- **WHEN** a Gantt drag changes `return_date` on a line with `rental_status='pickup'`
- **THEN** the dates are updated and rental prices are recalculated

### Requirement: Rental order views
The system SHALL provide sale order form/tree/search views with rental-specific fields: daterange widget for rental period, duration display, status badges (Booked/Late Pickup/Picked-up/Late Return/Returned), pickup/return action buttons, and "Update Rental Prices" button.

#### Scenario: Status badge display
- **WHEN** viewing a rental order in tree view
- **THEN** the rental_status field shows colored badges and next_action_date shows remaining days

### Requirement: Rental schedule Gantt view
The system SHALL provide a Gantt view on `sale.order.line` for the rental schedule, grouped by `product_id`, with `start_date` as date_start, `return_date` as date_stop, colored by `rental_color`, with consolidation on `product_uom_qty`.

#### Scenario: Schedule view
- **WHEN** opening the Rental Schedule menu
- **THEN** a Gantt chart displays rental lines as colored pills grouped by product, with a popover showing order number, pickup/return times, and status

#### Scenario: Create from empty cell
- **WHEN** a user clicks an empty cell in the schedule
- **THEN** a new rental order form opens with default dates and product from the cell context

### Requirement: Rental menus
The system SHALL provide an application menu "Rental" with submenus: Orders (all, customers), Schedule (Gantt), Products, Reporting, and Configuration (Settings, Rental Periods).

#### Scenario: App navigation
- **WHEN** a user opens the Rental app
- **THEN** the main menu displays Orders, Schedule, Products, Reporting, and Configuration sections
