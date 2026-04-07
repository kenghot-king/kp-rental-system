## ADDED Requirements

### Requirement: Condition selection on return wizard line
The return wizard line SHALL display a `condition` selection field with values `good` (default) and `damaged` when the wizard status is `return`.

#### Scenario: Default condition is good
- **WHEN** the return wizard opens
- **THEN** all wizard lines SHALL have condition set to `good`

#### Scenario: Staff marks item as damaged
- **WHEN** staff changes condition to `damaged` on a wizard line
- **THEN** the `damage_fee` (float) and `damage_reason` (text) fields SHALL become visible on that line

#### Scenario: Condition field hidden during pickup
- **WHEN** the wizard status is `pickup`
- **THEN** the condition, damage_fee, and damage_reason fields SHALL NOT be visible

### Requirement: Damage fee SO line creation
When a return is validated with damaged items, the system SHALL create a new SO line on the sales order for each wizard line with condition `damaged` and `damage_fee > 0`.

#### Scenario: Single damaged serial item
- **WHEN** staff returns SN001 with condition `damaged`, damage_fee `500`, reason `Cracked screen`
- **THEN** the system SHALL create an SO line with the damage fee service product, price_unit `500`, qty `1`, and description including the product name, serial number, and reason

#### Scenario: Bulk product with partial damage
- **WHEN** staff returns 7 units of a bulk product with condition `damaged`, damage_fee `150`, reason `Bent connectors`
- **THEN** the system SHALL create an SO line with the damage fee service product, price_unit `150`, qty `1`, and description including the product name and reason

#### Scenario: No damage fee entered
- **WHEN** staff marks condition as `damaged` but leaves damage_fee at `0`
- **THEN** the system SHALL NOT create a damage fee SO line (damage log is still created for serial products)

#### Scenario: Multiple damaged items in one return
- **WHEN** staff returns 3 items and marks 2 as damaged with different fees
- **THEN** the system SHALL create 2 separate damage fee SO lines, one per damaged wizard line

### Requirement: Damage fee is separate from deposit refund
The deposit credit note SHALL always refund the full proportional amount regardless of damage. Damage fees are independent charges.

#### Scenario: Return with damage — deposit still fully refunded
- **WHEN** staff returns 1 of 2 items with damage_fee `500` and deposit is `2000`
- **THEN** the deposit credit note SHALL be `1000` (1/2 × 2000) AND a separate damage fee SO line of `500` SHALL be created

#### Scenario: Damage fee exceeds deposit
- **WHEN** damage_fee is `3500` and total deposit is `2000`
- **THEN** the system SHALL allow the damage fee without cap AND the deposit credit note SHALL be created at full proportional amount

### Requirement: Damage fee service product
The system SHALL use a dedicated service product for damage fee SO lines, stored as `damage_product` on `res.company`.

#### Scenario: First damage fee — product auto-created
- **WHEN** a damage fee SO line is needed and `damage_product` is not set on the company
- **THEN** the system SHALL search for an existing product with `default_code='DAMAGE'` and `type='service'`, or create one named `Rental Damage Fee` with code `DAMAGE`

#### Scenario: Damage product configured in settings
- **WHEN** `damage_product` is set on the company
- **THEN** the system SHALL use that product for damage fee SO lines

### Requirement: Damage fee line description
The damage fee SO line description SHALL include the product name, reason, and serial number (if applicable).

#### Scenario: Serial-tracked product damage description
- **WHEN** damage fee line is created for serial-tracked product SN001 with reason `Cracked screen`
- **THEN** the SO line name SHALL follow format: `{product_name}\nS/N: {serial}\nReason: {reason}`

#### Scenario: Bulk product damage description
- **WHEN** damage fee line is created for a non-serial product with reason `Bent connectors`
- **THEN** the SO line name SHALL follow format: `{product_name}\nReason: {reason}`

### Requirement: Damage processing order in return wizard
The return wizard `_apply()` method SHALL process in this order: late fee → damage fee → qty_returned write (which triggers stock move + deposit credit note).

#### Scenario: Late and damaged return
- **WHEN** staff returns a late, damaged item
- **THEN** the system SHALL first create the delay cost SO line, then the damage fee SO line, then update qty_returned (triggering stock move and deposit credit note)
