## ADDED Requirements

### Requirement: Deposit validation before Send
The system SHALL check deposit sync before executing the Send action on a rental order.

#### Scenario: Deposits in sync — Send proceeds
- **WHEN** the user clicks [Send] on a rental order
- **AND** all rental lines have matching deposit lines (correct qty and price)
- **THEN** the Send action SHALL proceed normally

#### Scenario: Deposits out of sync — wizard shown before Send
- **WHEN** the user clicks [Send] on a rental order
- **AND** one or more rental lines have missing or mismatched deposit lines
- **THEN** the system SHALL open a wizard showing the mismatches
- **AND** the wizard SHALL offer [Update & Continue], [Continue As-Is], and [Cancel]

### Requirement: Deposit validation before Print
The system SHALL check deposit sync before executing the Print action on a rental order.

#### Scenario: Deposits out of sync — wizard shown before Print
- **WHEN** the user clicks [Print] on a rental order
- **AND** deposits are out of sync
- **THEN** the system SHALL open the deposit validation wizard

### Requirement: Deposit validation before Confirm
The system SHALL check deposit sync before executing the Confirm action on a rental order.

#### Scenario: Deposits out of sync — wizard shown before Confirm
- **WHEN** the user clicks [Confirm] on a rental order
- **AND** deposits are out of sync
- **THEN** the system SHALL open the deposit validation wizard

### Requirement: Deposit validation before Preview
The system SHALL check deposit sync before executing the Preview action on a rental order.

#### Scenario: Deposits out of sync — wizard shown before Preview
- **WHEN** the user clicks [Preview] on a rental order
- **AND** deposits are out of sync
- **THEN** the system SHALL open the deposit validation wizard

### Requirement: No validation on Cancel
The system SHALL NOT check deposit sync when the user clicks [Cancel].

#### Scenario: Cancel proceeds without validation
- **WHEN** the user clicks [Cancel] on a rental order
- **THEN** the cancellation SHALL proceed without deposit validation

### Requirement: Wizard Update & Continue action
The wizard SHALL provide an [Update & Continue] button that syncs deposits then executes the original action.

#### Scenario: User clicks Update & Continue
- **WHEN** the deposit validation wizard is shown for a Confirm action
- **AND** the user clicks [Update & Continue]
- **THEN** the system SHALL call `action_sync_deposits()` to sync all deposit lines
- **AND** THEN execute the Confirm action

### Requirement: Wizard Continue As-Is action
The wizard SHALL provide a [Continue As-Is] button that executes the original action without modifying deposits.

#### Scenario: User clicks Continue As-Is
- **WHEN** the deposit validation wizard is shown
- **AND** the user clicks [Continue As-Is]
- **THEN** the system SHALL execute the original action without modifying deposit lines

### Requirement: Wizard Cancel action
The wizard SHALL provide a [Cancel] button that closes the wizard and returns to the order.

#### Scenario: User clicks Cancel
- **WHEN** the deposit validation wizard is shown
- **AND** the user clicks [Cancel]
- **THEN** the wizard SHALL close and return to the rental order without any action

### Requirement: Wizard displays mismatch details
The wizard SHALL display human-readable information about what is out of sync.

#### Scenario: Multiple mismatches displayed
- **WHEN** the wizard opens with mismatches
- **THEN** it SHALL display each mismatch (e.g., "Power Bank: no deposit line", "Excavator: qty 2 → 4")
