## ADDED Requirements

### Requirement: Hold payment created in processing state
When staff registers a payment on a deposit invoice using an HLD journal, the system SHALL create an `account.payment` with `is_deposit_hold=True` and `state='processing'`. No journal entry SHALL be created. The payment SHALL store `approval_code` and `ref_2` fields.

#### Scenario: Hold payment created without journal entry
- **WHEN** staff registers payment on a deposit invoice using a journal where `for_hold=True`
- **THEN** an `account.payment` record is created with `is_deposit_hold=True`, `state='processing'`
- **THEN** no `account.move.line` journal entries are created for this payment

#### Scenario: Approval code stored
- **WHEN** staff enters an approval code during hold payment registration
- **THEN** the value is stored in `approval_code` on the `account.payment` record

### Requirement: Forfeit flow posts hold payment and reconciles deposit invoice
When staff forfeits a hold (customer no-show), the system SHALL update the payment date to the forfeiture date, post the hold payment (creating a journal entry), and reconcile it against the deposit invoice.

#### Scenario: Forfeit marks deposit invoice as paid
- **WHEN** staff confirms a forfeiture date via the forfeit wizard
- **THEN** the hold payment `state` becomes `posted`
- **THEN** the deposit invoice `payment_state` becomes `paid`
- **THEN** the hold payment is reconciled against the deposit invoice

#### Scenario: Forfeiture date applied to payment
- **WHEN** staff enters a forfeiture date different from today
- **THEN** the hold payment `date` is updated to the entered forfeiture date before posting

### Requirement: Unhold releases hold and returns invoice to not_paid
When staff clicks Unhold, the system SHALL revert the hold payment to `draft` state and clear the `deposit_hold_state` on the deposit invoice. The invoice SHALL return to `payment_state='not_paid'`.

#### Scenario: Unhold clears hold state
- **WHEN** staff clicks Unhold on a deposit invoice with `deposit_hold_state='hold'`
- **THEN** the hold payment `state` becomes `draft`
- **THEN** the deposit invoice `deposit_hold_state` becomes `none`
- **THEN** the deposit invoice `payment_state` remains `not_paid`

### Requirement: Hold payment cancelled after CN reconciliation
After unhold, when the deposit credit note is created and reconciled, the system SHALL set the hold payment `state` to `cancel`. The record SHALL NOT be deleted.

#### Scenario: Hold payment cancelled not deleted
- **WHEN** the deposit credit note is reconciled against the deposit invoice after an unhold
- **THEN** the previously-unheld hold payment `state` becomes `cancel`
- **THEN** the `account.payment` record still exists in the database
- **THEN** `approval_code` and `ref_2` values are preserved on the record

### Requirement: Normal action_post blocked for hold payments
The system SHALL prevent `account.payment.action_post()` from being called directly on a payment with `is_deposit_hold=True`, unless called from the forfeit flow.

#### Scenario: Direct post blocked
- **WHEN** `action_post()` is called on an `account.payment` with `is_deposit_hold=True` outside the forfeit flow
- **THEN** the system raises a `UserError` and the payment is not posted

### Requirement: CN creation skipped during active hold
The system SHALL skip creating a deposit credit note when the deposit invoice `deposit_hold_state` is `'hold'`.

#### Scenario: CN skipped while hold active
- **WHEN** `_create_deposit_credit_note()` is triggered on a sale order line
- **THEN** if the deposit invoice `deposit_hold_state == 'hold'`, no credit note is created
