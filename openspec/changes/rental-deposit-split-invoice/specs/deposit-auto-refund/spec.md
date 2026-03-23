## ADDED Requirements

### Requirement: Auto-create credit note on return
The system SHALL automatically create and post a credit note for the deposit when rental items are returned.

#### Scenario: Full return
- **WHEN** all rented items on a SO line are returned
- **AND** a deposit line exists on the same SO with a posted invoice
- **THEN** the system creates a credit note for the full deposit amount
- **AND** the credit note is auto-posted

#### Scenario: Partial return
- **WHEN** a subset of rented items on a SO line are returned
- **AND** a deposit line exists on the same SO with a posted invoice
- **THEN** the system creates a credit note for a proportional amount: `(qty_returned / qty_delivered) × deposit_invoice_amount`
- **AND** the credit note is auto-posted

#### Scenario: Multiple partial returns
- **WHEN** items are returned across multiple return events
- **THEN** each return event creates its own credit note for the proportional amount of that return
- **AND** the total credited across all returns SHALL NOT exceed the original deposit invoice amount

### Requirement: No credit note without posted deposit invoice
The system SHALL NOT create a credit note if the deposit line has not been invoiced or the deposit invoice is not posted.

#### Scenario: Deposit not yet invoiced
- **WHEN** rental items are returned
- **AND** no posted invoice exists for the deposit line
- **THEN** no credit note is created

### Requirement: Credit note references deposit invoice
Each auto-generated credit note SHALL reference the original deposit invoice via `reversed_entry_id`.

#### Scenario: Credit note traceability
- **WHEN** a deposit credit note is created
- **THEN** the credit note's `reversed_entry_id` points to the original deposit invoice
- **AND** the credit note is linked to the sale order
