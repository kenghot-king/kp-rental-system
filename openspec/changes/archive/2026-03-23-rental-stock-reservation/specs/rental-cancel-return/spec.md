## ADDED Requirements

### Requirement: Auto-return stock on SO cancellation after pickup
When a rental SO is cancelled after pickup has occurred, the system SHALL automatically create and validate a return move for any outstanding rented quantity (qty_delivered - qty_returned) to bring stock back from the Rental Location to WH/Stock.

#### Scenario: Cancel SO after full pickup, no returns yet
- **WHEN** a rental SO with qty_delivered = 3 and qty_returned = 0 is cancelled
- **THEN** a return picking is created (Rental Location → WH/Stock) with qty = 3
- **THEN** the picking is validated immediately
- **THEN** On Hand increases by 3

#### Scenario: Cancel SO after partial return
- **WHEN** a rental SO with qty_delivered = 3 and qty_returned = 1 is cancelled
- **THEN** a return picking is created with qty = 2 (3 - 1)
- **THEN** On Hand increases by 2

#### Scenario: Cancel SO after full return
- **WHEN** a rental SO with qty_delivered = 3 and qty_returned = 3 is cancelled
- **THEN** no return picking is created (all stock already returned)

#### Scenario: Cancel SO before pickup
- **WHEN** a confirmed rental SO (not yet picked up) is cancelled
- **THEN** the delivery picking is cancelled by standard sale_stock behavior
- **THEN** stock reservation is released, Free to Use increases back

#### Scenario: Cancel SO with serial-tracked product after pickup
- **WHEN** a rental SO with pickedup_lot_ids = [SN001, SN002] and returned_lot_ids = [SN001] is cancelled
- **THEN** a return picking is created for the outstanding lot [SN002]
- **THEN** SN002 moves from Rental Location back to WH/Stock
