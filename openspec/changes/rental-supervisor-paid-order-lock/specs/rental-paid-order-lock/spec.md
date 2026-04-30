## ADDED Requirements

### Requirement: Rental order lines are locked after payment for non-supervisors
Once any `out_invoice` on a rental order reaches `payment_state` of `paid` or `in_payment`, the system SHALL make rental item lines and deposit lines read-only in the order form for users who do not belong to `ggg_rental.group_rental_supervisor`. Late fine lines and damage charge lines SHALL remain editable regardless of payment state.

#### Scenario: Regular user cannot edit rental item after payment
- **WHEN** a rental order has a posted invoice with `payment_state = paid`
- **AND** the current user is not a Rental Supervisor
- **THEN** fields on lines where `is_rental = True` SHALL be read-only (`product_id`, `product_template_id`, `name`, `product_uom_qty`, `price_unit`, `discount`, `product_uom_id`, `tax_ids`)

#### Scenario: Regular user cannot edit deposit line after payment
- **WHEN** a rental order has a posted invoice with `payment_state = paid`
- **AND** the current user is not a Rental Supervisor
- **THEN** fields on lines where `deposit_parent_id` is set SHALL be read-only

#### Scenario: Regular user can edit deposit line before payment
- **WHEN** a rental order has no posted invoice with `payment_state` in `(paid, in_payment)`
- **AND** the current user is not a Rental Supervisor
- **THEN** deposit line fields SHALL be editable

#### Scenario: Late fine line stays editable after payment
- **WHEN** a rental order has a posted paid invoice
- **AND** the current user is not a Rental Supervisor
- **THEN** lines where `is_rental = False` and `deposit_parent_id` is not set SHALL remain editable

#### Scenario: Damage charge line stays editable after payment
- **WHEN** a rental order has a posted paid invoice
- **AND** the current user is not a Rental Supervisor
- **THEN** damage charge lines (generated via `_generate_damage_line`) SHALL remain editable

### Requirement: Rental Supervisor can edit all lines on paid orders
A user belonging to `ggg_rental.group_rental_supervisor` SHALL be able to edit rental item lines and deposit lines on a paid rental order without restriction.

#### Scenario: Supervisor edits rental item line on paid order
- **WHEN** a rental order has a posted paid invoice
- **AND** the current user is a Rental Supervisor
- **THEN** all order line fields SHALL be editable including rental items and deposit lines

### Requirement: Cancellation is blocked when any invoice is paid
The system SHALL prevent cancellation of a rental order if any `out_invoice` on that order has `payment_state` in `(paid, in_payment)`. This restriction applies to all users including Rental Supervisors. The user must refund all paid invoices before cancellation is permitted.

#### Scenario: Regular user cannot cancel paid rental order
- **WHEN** a rental order has a posted invoice with `payment_state = paid`
- **AND** the current user attempts to cancel the order
- **THEN** the system SHALL raise a `UserError` with a message directing the user to refund all paid invoices first

#### Scenario: Supervisor cannot cancel paid rental order without refund
- **WHEN** a rental order has a posted invoice with `payment_state = paid`
- **AND** the current user is a Rental Supervisor
- **AND** the user attempts to cancel the order
- **THEN** the system SHALL raise a `UserError` — supervisor must refund first

#### Scenario: Cancel button hidden when order is paid
- **WHEN** a rental order has a posted paid invoice
- **THEN** the Cancel button SHALL not be visible in the form view for any user

#### Scenario: Cancel allowed after full refund
- **WHEN** all paid invoices on a rental order have been fully refunded (credit notes applied, `payment_state` no longer `paid` or `in_payment`)
- **THEN** cancellation SHALL be permitted and the Cancel button SHALL be visible again

#### Scenario: Cancel remains available for non-rental orders
- **WHEN** a sale order has `is_rental_order = False`
- **THEN** cancellation behavior SHALL be unchanged regardless of invoice payment state
