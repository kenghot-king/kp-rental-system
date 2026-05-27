## ADDED Requirements

### Requirement: Journal has for_hold flag
`account.journal` SHALL have a boolean field `for_hold` that marks it as a credit hold journal (HLD type). Default is `False`.

#### Scenario: for_hold field exists
- **WHEN** viewing an account journal configuration
- **THEN** a `for_hold` boolean field is present and configurable

### Requirement: HLD journal blocked on rental invoices
When staff attempts to register a payment on a rental invoice (non-deposit) using a journal with `for_hold=True`, the system SHALL raise an error and prevent the payment.

#### Scenario: HLD blocked on rental invoice
- **WHEN** staff registers a payment on a rental invoice using a journal with `for_hold=True`
- **THEN** the system raises a `UserError`
- **THEN** no payment is created

#### Scenario: HLD allowed on deposit invoice
- **WHEN** staff registers a payment on a deposit invoice using a journal with `for_hold=True`
- **THEN** the system creates a hold payment in `processing` state without error

### Requirement: EDC journal allowed on both invoice types
A journal with `for_hold=False` (EDC) SHALL be allowed on both rental invoices and deposit invoices, following the standard Odoo payment flow.

#### Scenario: EDC on rental invoice proceeds normally
- **WHEN** staff registers a payment on a rental invoice using a journal with `for_hold=False`
- **THEN** a standard `account.payment` is posted immediately with a journal entry
