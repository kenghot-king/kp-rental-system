## MODIFIED Requirements

### Requirement: Completion status displayed in views
The system SHALL display the `rental_completion` field as a badge in Kanban, List, and Form views of rental orders. The badge SHALL be clickable and SHALL open a popover containing the `rental_completion_detail` breakdown when clicked.

#### Scenario: Badge visibility on confirmed rental order
- **WHEN** viewing a confirmed rental order (`state='sale'`, `is_rental_order=True`) in Kanban, List, or Form view
- **THEN** the completion badge SHALL be visible with value "Complete" (green) or "Incomplete" (red/orange)

#### Scenario: Badge hidden on non-rental order
- **WHEN** viewing a non-rental order or an unconfirmed rental order
- **THEN** the completion badge SHALL NOT be displayed

#### Scenario: Click opens detail popover on incomplete status
- **WHEN** user clicks an "Incomplete" badge
- **THEN** a popover SHALL open adjacent to the badge showing the completion detail breakdown (Returned, Paid, Deposit refunded) with one line per axis

#### Scenario: Click shows confirmation on complete status
- **WHEN** user clicks a "Complete" badge
- **THEN** a popover SHALL open showing a confirmation message (e.g. "All conditions met")

#### Scenario: Popover dismissal
- **WHEN** a popover is open AND the user clicks outside, presses Escape, or clicks the badge again
- **THEN** the popover SHALL close

#### Scenario: Keyboard accessibility
- **WHEN** the badge is focused and the user presses Enter or Space
- **THEN** the popover SHALL toggle (open if closed, close if open)
