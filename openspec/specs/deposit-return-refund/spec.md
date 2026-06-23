## ADDED Requirements

### Requirement: Deposit refund on return depends on deposit type

On Return, the system SHALL create and auto-refund a deposit credit note only when the deposit was
paid in cash (the deposit invoice has a real outstanding residual to refund). A held deposit —
whether released (unhold) or forfeited — SHALL NOT produce a credit note on return.

#### Scenario: Cash-paid deposit is refunded
- **WHEN** an order with a cash-paid deposit is returned
- **THEN** the system SHALL create a deposit credit note and auto-refund it according to the proportion returned

#### Scenario: Released hold produces no credit note
- **WHEN** an order whose deposit hold was released (unhold) is returned
- **THEN** the system SHALL NOT create a deposit credit note

#### Scenario: Forfeited deposit produces no credit note
- **WHEN** an order whose deposit hold was forfeited is returned
- **THEN** the system SHALL NOT create a deposit credit note

#### Scenario: Return does not crash on a held deposit
- **WHEN** an order with a held deposit is returned
- **THEN** the Return SHALL complete without raising "There's nothing left to pay for the selected journal items"
