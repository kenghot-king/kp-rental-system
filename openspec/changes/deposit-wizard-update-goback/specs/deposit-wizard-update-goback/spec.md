## ADDED Requirements

### Requirement: Update & Go Back button on deposit wizard
The deposit validation wizard SHALL provide an [Update & Go Back] button that syncs deposits and returns the user to the order form.

#### Scenario: User clicks Update & Go Back
- **WHEN** the deposit validation wizard is shown
- **AND** the user clicks [Update & Go Back]
- **THEN** the system SHALL call `action_sync_deposits()` to sync all deposit lines
- **AND** close the wizard, returning the user to the rental order form
- **AND** the original action (Send/Confirm/etc.) SHALL NOT be executed
