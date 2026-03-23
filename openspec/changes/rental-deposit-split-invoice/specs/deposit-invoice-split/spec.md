## ADDED Requirements

### Requirement: Separate invoices for deposit and rental lines
The system SHALL create separate invoices for deposit lines and non-deposit lines when invoicing a sale order.

#### Scenario: SO with both rental and deposit lines
- **WHEN** user creates an invoice for a sale order containing both rental product lines and deposit product lines
- **THEN** the system creates two invoices: one containing only deposit lines, one containing only rental lines

#### Scenario: SO with only rental lines
- **WHEN** user creates an invoice for a sale order with no deposit product lines
- **THEN** the system creates a single invoice as normal (no behavioral change)

#### Scenario: SO with only deposit lines
- **WHEN** user creates an invoice for a sale order with only deposit product lines
- **THEN** the system creates a single invoice containing the deposit lines

### Requirement: Invoice split uses native grouping mechanism
The system SHALL implement the split by overriding `_get_invoice_grouping_keys()` on `sale.order` to include a deposit indicator key.

#### Scenario: Grouping key includes deposit flag
- **WHEN** the invoicing process groups SO lines
- **THEN** lines with `product_id.is_rental_deposit = True` are grouped separately from lines with `is_rental_deposit = False`
