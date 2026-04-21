## ADDED Requirements

### Requirement: Journal channel classification

The system SHALL provide a `channel_type` selection field on `account.journal` with values `cash`, `edc`, `qr`, `online`, and `other`. The field SHALL be optional (a journal may leave it unset), administrator-configured, and used for reporting and grouping only — it SHALL NOT drive any user-facing field visibility or validation on payment forms or wizards.

#### Scenario: Admin categorizes a cash journal
- **WHEN** an administrator edits a Cash journal and sets `channel_type = 'cash'`
- **THEN** the value SHALL be saved on the journal record and available as a reporting filter

#### Scenario: Admin categorizes an EDC journal
- **WHEN** an administrator edits a bank journal representing an EDC terminal (e.g. "EDC-KBank-Silom-T1") and sets `channel_type = 'edc'`
- **THEN** the value SHALL be saved on the journal record and available as a reporting filter

#### Scenario: Unset channel_type does not affect existing behavior
- **WHEN** a journal has `channel_type` left empty
- **THEN** payments on that journal SHALL still be creatable and editable with no errors, and the journal SHALL simply be excluded from channel-based reports

### Requirement: Cashier attribution on payments

The system SHALL provide a `cashier_id` Many2one field to `res.users` on `account.payment` that identifies the user who collected the payment. The value SHALL default to the current user (`env.user`) when a payment is registered through the `account.payment.register` wizard, and SHALL NOT be editable from the register wizard.

#### Scenario: Cashier auto-populated from register wizard
- **WHEN** a logged-in user registers payment for a rental invoice via the Pay wizard
- **THEN** the created `account.payment` record SHALL have `cashier_id` set to that user

#### Scenario: Cashier field visible on payment form
- **WHEN** a staff member views an `account.payment` record
- **THEN** the `cashier_id` field SHALL be visible on the payment form

#### Scenario: Cashier field cannot be overridden in register wizard
- **WHEN** a staff member opens the Pay wizard
- **THEN** the wizard SHALL NOT expose `cashier_id` as an editable input (it is auto-populated server-side to `env.user`)

### Requirement: Approval code metadata on payments

The system SHALL provide an `approval_code` Char field on `account.payment` that captures free-text metadata such as EDC approval codes, QR transaction IDs, or online gateway references. The field SHALL be always visible on the payment form and on the `account.payment.register` wizard, SHALL NOT be required, and SHALL NOT be conditioned on `channel_type`.

#### Scenario: Approval code entered at payment registration
- **WHEN** staff registers payment for a rental invoice and enters a value in `approval_code`
- **THEN** the created `account.payment` SHALL contain that value in its `approval_code` field

#### Scenario: Approval code left empty
- **WHEN** staff registers payment and leaves `approval_code` empty
- **THEN** the payment SHALL be created successfully with `approval_code` empty

#### Scenario: Approval code visible regardless of journal
- **WHEN** staff opens the Pay wizard with any journal selected (Cash, EDC, QR, Online, Other)
- **THEN** the `approval_code` field SHALL be visible and editable

### Requirement: Computed display method

The system SHALL provide a stored computed Char field `display_method` on `account.payment` that equals the `name` of the selected `payment_method_line_id`. This field SHALL be used as the primary grouping key for payment reports and downstream reconciliation lines.

#### Scenario: Display method reflects method line name
- **WHEN** a payment is created with `payment_method_line_id` whose `name` is "VISA"
- **THEN** the payment's `display_method` SHALL equal "VISA"

#### Scenario: Display method updates when method line name changes
- **WHEN** an administrator renames a payment method line from "VISA" to "VISA Card"
- **THEN** the `display_method` on existing payments using that line SHALL recompute to "VISA Card" on next recomputation trigger

#### Scenario: Display method empty when no method line set
- **WHEN** a payment has no `payment_method_line_id`
- **THEN** `display_method` SHALL be empty (not raise an error)

### Requirement: Register wizard passthrough

The system SHALL extend `account.payment.register` to auto-populate `cashier_id` from `env.user` and expose `approval_code` for entry. Values SHALL be passed through to the created `account.payment` record. The wizard SHALL continue to show existing `payment_reference` and `payment_reference_2` fields as defined by the `rental-payment-refs` capability, unchanged.

#### Scenario: Wizard populates cashier and approval code onto payment
- **WHEN** staff registers payment through the wizard and fills `approval_code`
- **THEN** the created `account.payment` SHALL have `cashier_id = env.user` and `approval_code` matching the entered value

#### Scenario: Wizard coexists with rental-payment-refs fields
- **WHEN** staff opens the Pay wizard for a rental invoice
- **THEN** the wizard SHALL show `payment_reference`, `payment_reference_2`, `approval_code`, and SHALL NOT expose `cashier_id` as an editable input
