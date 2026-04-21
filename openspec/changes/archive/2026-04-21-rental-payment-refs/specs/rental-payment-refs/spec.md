## ADDED Requirements

### Requirement: Payment reference fields on rental payments
The system SHALL display two reference fields (Reference 1, Reference 2) on `account.payment` records that are linked to rental orders. These fields SHALL NOT be visible on non-rental payments.

#### Scenario: Rental payment shows reference fields
- **WHEN** a payment is linked to an invoice originating from a rental sale order
- **THEN** the payment form SHALL display "Reference 1" (`payment_reference`) and "Reference 2" (`payment_reference_2`) fields

#### Scenario: Non-rental payment hides reference fields
- **WHEN** a payment is linked to a non-rental invoice or no invoice
- **THEN** the payment form SHALL NOT display "Reference 1" or "Reference 2" fields

### Requirement: Rental payment detection
The system SHALL provide a computed boolean `is_rental_payment` on `account.payment` that determines whether the payment is related to a rental order.

#### Scenario: Payment linked to rental invoice
- **WHEN** a payment is reconciled with an invoice that originates from a sale order where `is_rental_order = True`
- **THEN** `is_rental_payment` SHALL be `True`

#### Scenario: Payment not linked to rental
- **WHEN** a payment is not reconciled with any rental-origin invoice
- **THEN** `is_rental_payment` SHALL be `False`

### Requirement: Reference fields in payment register wizard
The system SHALL display Reference 1 and Reference 2 fields in the `account.payment.register` wizard when registering payment for a rental invoice. Values entered SHALL be passed through to the created `account.payment` record.

#### Scenario: Register payment with references
- **WHEN** staff registers a payment from a rental invoice and enters values in Reference 1 and Reference 2
- **THEN** the created `account.payment` record SHALL contain those reference values

#### Scenario: Register payment without references
- **WHEN** staff registers a payment and leaves reference fields empty
- **THEN** the payment SHALL be created successfully with empty reference fields
