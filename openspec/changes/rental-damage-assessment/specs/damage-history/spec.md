## ADDED Requirements

### Requirement: Damage log model
The system SHALL provide a `rental.damage.log` model to record damage events with the following fields:
- `lot_id` (Many2one → stock.lot, optional): the damaged serial number
- `order_id` (Many2one → sale.order, required): the rental order
- `order_line_id` (Many2one → sale.order.line, required): the rental order line
- `product_id` (Many2one → product.product, required): the damaged product
- `damage_fee` (Float): the assessed damage fee amount
- `reason` (Text): staff-entered damage description
- `date` (Datetime, default=now): when the damage was assessed
- `user_id` (Many2one → res.users, default=current user): who assessed the damage

#### Scenario: Damage log created for serial product
- **WHEN** staff returns serial SN001 with condition `damaged`, fee `500`, reason `Cracked screen`
- **THEN** the system SHALL create a `rental.damage.log` record with `lot_id=SN001`, `damage_fee=500`, `reason='Cracked screen'`, `order_id`, `order_line_id`, `product_id`, `date=now`, and `user_id=current user`

#### Scenario: Damage log created for bulk product
- **WHEN** staff returns a non-serial product with condition `damaged`, fee `150`, reason `Bent connectors`
- **THEN** the system SHALL create a `rental.damage.log` record with `lot_id=False`, and all other fields populated

#### Scenario: No damage log when condition is good
- **WHEN** staff returns an item with condition `good`
- **THEN** the system SHALL NOT create a `rental.damage.log` record

### Requirement: Damage history on stock.lot
The `stock.lot` model SHALL have a `damage_log_ids` One2many field linking to `rental.damage.log` records, and a computed `damage_count` integer field.

#### Scenario: Serial with damage history
- **WHEN** viewing a `stock.lot` record that has 3 associated damage log entries
- **THEN** `damage_count` SHALL be `3` and `damage_log_ids` SHALL contain those 3 records

### Requirement: Damage history smart button on stock.lot form
The `stock.lot` form view SHALL display a smart button showing the damage count, linking to the list of damage log records for that serial.

#### Scenario: Smart button visible with damage history
- **WHEN** viewing a `stock.lot` form where `damage_count > 0`
- **THEN** a smart button SHALL display showing the damage count (e.g., "2 Damages") and clicking it SHALL open the damage log list filtered to that lot

#### Scenario: Smart button hidden when no damage
- **WHEN** viewing a `stock.lot` form where `damage_count == 0`
- **THEN** the damage smart button SHALL NOT be visible

### Requirement: Damage log list and form views
The `rental.damage.log` model SHALL have list and form views displaying all fields with appropriate grouping and search options.

#### Scenario: Damage log list view
- **WHEN** viewing the damage log list (from smart button or menu)
- **THEN** the list SHALL show columns: date, order_id, product_id, lot_id, damage_fee, reason, user_id

#### Scenario: Damage log searchable by product and order
- **WHEN** searching damage logs
- **THEN** the user SHALL be able to filter by product_id, lot_id, order_id, and date range
