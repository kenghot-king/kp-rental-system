## ADDED Requirements

### Requirement: Deposit product identification
The system SHALL identify deposit products via the is_rental_deposit flag on product.template.

#### Scenario: TC-DP-001 Mark product as deposit
- **WHEN** admin sets is_rental_deposit=True on a service product
- **THEN** product is recognized as a deposit product in rental orders

### Requirement: Split invoicing for mixed orders
The system SHALL create separate invoices when an order contains both deposit and non-deposit lines.

#### Scenario: TC-DP-002 Mixed order creates two invoices
- **WHEN** order has rental lines (equipment) + deposit line, user clicks "Create Invoice"
- **THEN** system creates 2 invoices: one for deposit only, one for rental lines only

#### Scenario: TC-DP-003 Rental-only order creates single invoice
- **WHEN** order has only rental lines (no deposit), user creates invoice
- **THEN** system creates 1 invoice with all rental lines

#### Scenario: TC-DP-004 Deposit-only order creates single invoice
- **WHEN** order has only deposit line, user creates invoice
- **THEN** system creates 1 invoice with deposit line only

### Requirement: Deposit credit note on return
The system SHALL create a proportional credit note for the deposit when items are returned.

#### Scenario: TC-DP-005 Full return — full deposit refund
- **WHEN** order has deposit=1000 THB, all items returned (qty_returned = qty_delivered)
- **THEN** credit note created for 1000 THB linked to original deposit invoice

#### Scenario: TC-DP-006 Partial return — proportional deposit refund
- **WHEN** order has deposit=1000 THB, 3 of 5 items returned
- **THEN** credit note created for 600 THB (3/5 × 1000)

#### Scenario: TC-DP-007 Second partial return — additional credit note
- **WHEN** first return: 3/5 items (credit note 600). Second return: 2/5 items
- **THEN** second credit note for 400 THB (2/5 × 1000). Total refunded = 1000

### Requirement: Auto-refund deposit payment
The system SHALL optionally auto-register a refund payment when deposit credit note is created.

#### Scenario: TC-DP-008 Auto-refund enabled
- **WHEN** company.deposit_auto_refund=True, deposit credit note is created
- **THEN** system automatically registers a payment on the credit note

#### Scenario: TC-DP-009 Auto-refund disabled
- **WHEN** company.deposit_auto_refund=False, deposit credit note is created
- **THEN** credit note is created but no payment is registered (staff must process manually)

#### Scenario: TC-DP-010 Configure auto-refund in settings
- **WHEN** admin toggles "Auto Refund Deposit" in Settings
- **THEN** setting is saved and applies to subsequent returns
