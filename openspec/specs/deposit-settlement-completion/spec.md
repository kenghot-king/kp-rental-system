## ADDED Requirements

### Requirement: Unhold and forfeit settle the deposit for completion

An order's deposit-settlement axis SHALL be satisfied when the deposit is unheld (hold released) or
forfeited (deposit invoice paid), in addition to being refunded via credit note. A held deposit that
is still active SHALL NOT count as settled.

#### Scenario: Unhold settles the deposit
- **WHEN** a deposit hold is released (unhold)
- **THEN** the order's deposit-settlement axis SHALL count that deposit as settled

#### Scenario: Forfeit settles the deposit
- **WHEN** a deposit hold is forfeited and the deposit invoice becomes paid
- **THEN** the order's deposit-settlement axis SHALL count that deposit as settled

#### Scenario: Active hold is not settled
- **WHEN** a deposit hold is still active (neither released nor forfeited)
- **THEN** the order's deposit-settlement axis SHALL NOT count that deposit as settled

#### Scenario: Order reaches Complete when all axes satisfied
- **WHEN** all items are returned, all non-deposit invoices are paid, and the deposit is settled by unhold or forfeit
- **THEN** the order's completion status SHALL be Complete
