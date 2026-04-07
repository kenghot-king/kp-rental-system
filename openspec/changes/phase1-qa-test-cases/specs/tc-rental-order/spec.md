## ADDED Requirements

### Requirement: Create rental order with valid dates
The system SHALL allow creating a rental order with rental_start_date and rental_return_date, and compute duration_days and remaining_hours correctly.

#### Scenario: TC-RO-001 Create rental order with dates
- **WHEN** user creates a new rental order and sets start_date=2026-04-10 09:00 and return_date=2026-04-12 09:00
- **THEN** order is created with duration_days=2, remaining_hours=0, rental_status=draft

#### Scenario: TC-RO-002 Auto-set dates if not provided
- **WHEN** user creates a rental order without setting dates and adds a rental product line
- **THEN** system auto-sets start_date=now+1hr, return_date=now+25hrs

#### Scenario: TC-RO-003 Invalid dates rejected
- **WHEN** user sets return_date earlier than or equal to start_date
- **THEN** system raises a validation error

#### Scenario: TC-RO-004 Duration with remaining hours
- **WHEN** user sets start_date=2026-04-10 09:00 and return_date=2026-04-12 14:00
- **THEN** duration_days=2, remaining_hours=5

### Requirement: Rental order status transitions
The system SHALL transition rental_status through the correct lifecycle: draft → sent → pickup → return → returned.

#### Scenario: TC-RO-005 Draft to sent
- **WHEN** user sends quotation (action_quotation_sent)
- **THEN** rental_status changes to "sent"

#### Scenario: TC-RO-006 Sent to pickup on confirm
- **WHEN** user confirms the quotation (action_confirm)
- **THEN** rental_status changes to "pickup", delivery stock move is created

#### Scenario: TC-RO-007 Pickup to return after full pickup
- **WHEN** all items are picked up via the pickup wizard
- **THEN** rental_status changes to "return"

#### Scenario: TC-RO-008 Return to returned after full return
- **WHEN** all picked-up items are returned via the return wizard
- **THEN** rental_status changes to "returned"

#### Scenario: TC-RO-009 Partial pickup stays in pickup
- **WHEN** only some items are picked up (qty_delivered < product_uom_qty)
- **THEN** rental_status remains "pickup", has_pickable_lines=True

#### Scenario: TC-RO-010 Partial return stays in return
- **WHEN** some items are returned but not all (qty_returned < qty_delivered)
- **THEN** rental_status remains "return", has_returnable_lines=True

### Requirement: Cancel rental order with active rentals
The system SHALL auto-return rented items when a rental order with picked-up items is cancelled.

#### Scenario: TC-RO-011 Cancel with picked-up items
- **WHEN** user cancels a rental order that has items currently picked up (qty_delivered > qty_returned)
- **THEN** system auto-returns all outstanding items, creates return stock moves, and sets state to cancel

#### Scenario: TC-RO-012 Cancel draft order
- **WHEN** user cancels a draft rental order (no items picked up)
- **THEN** order is cancelled without stock moves

### Requirement: Late order detection
The system SHALL mark orders as late when current time exceeds the next action date.

#### Scenario: TC-RO-013 Late pickup detected
- **WHEN** rental_status=pickup and now > rental_start_date
- **THEN** is_late=True, status badge shows "Late Pickup"

#### Scenario: TC-RO-014 Late return detected
- **WHEN** rental_status=return and now > rental_return_date
- **THEN** is_late=True, status badge shows "Late Return"

#### Scenario: TC-RO-015 On-time order not marked late
- **WHEN** rental_status=pickup and now < rental_start_date
- **THEN** is_late=False

### Requirement: Update rental prices on date change
The system SHALL recalculate all rental line prices when dates are changed.

#### Scenario: TC-RO-016 Extend rental period
- **WHEN** user changes return_date from 2026-04-12 to 2026-04-15 and clicks "Update Rental Prices"
- **THEN** all rental line prices recalculate based on new 5-day duration

#### Scenario: TC-RO-017 Shorten rental period
- **WHEN** user changes return_date to reduce duration from 7 days to 3 days and clicks "Update Rental Prices"
- **THEN** rental line prices decrease accordingly
