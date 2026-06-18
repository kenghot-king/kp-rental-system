## ADDED Requirements

### Requirement: Deposit invoice shows On Hold badge when hold is active
When a deposit invoice has an active hold payment (`deposit_hold_state='hold'`), the invoice form SHALL display an "On Hold" badge.

#### Scenario: On Hold badge visible
- **WHEN** a deposit invoice has `deposit_hold_state='hold'`
- **THEN** an "On Hold" status badge is displayed on the invoice form view

#### Scenario: On Hold badge hidden when no active hold
- **WHEN** a deposit invoice has `deposit_hold_state='none'`
- **THEN** no "On Hold" badge is displayed

### Requirement: Deposit invoice shows Unhold and Forfeit buttons when hold is active
When `deposit_hold_state='hold'`, the deposit invoice SHALL show an Unhold button and a Forfeit button. These buttons SHALL be hidden when there is no active hold.

#### Scenario: Unhold and Forfeit buttons visible
- **WHEN** a deposit invoice has `deposit_hold_state='hold'`
- **THEN** both "Unhold" and "Forfeit" action buttons are visible on the form

#### Scenario: Buttons hidden when not on hold
- **WHEN** a deposit invoice has `deposit_hold_state='none'`
- **THEN** neither Unhold nor Forfeit buttons are visible

### Requirement: Forfeit wizard captures forfeiture date
Clicking Forfeit SHALL open a wizard dialog where staff enters the forfeiture date. The default value SHALL be today's date.

#### Scenario: Wizard opens with today as default
- **WHEN** staff clicks the Forfeit button
- **THEN** a wizard dialog opens with a date field pre-filled with today's date

#### Scenario: Staff can override forfeiture date
- **WHEN** staff changes the date in the wizard and confirms
- **THEN** the forfeiture flow proceeds with the entered date

### Requirement: Deposit Certificate printable for HLD holds
When a deposit invoice is in hold state, staff SHALL be able to print a ใบมัดจำ (Deposit Certificate) document.

#### Scenario: Print Deposit Certificate available
- **WHEN** a deposit invoice has `deposit_hold_state='hold'`
- **THEN** a "Print Deposit Certificate" action is available on the invoice
- **THEN** the printed document shows the hold amount, approval code, and customer details
