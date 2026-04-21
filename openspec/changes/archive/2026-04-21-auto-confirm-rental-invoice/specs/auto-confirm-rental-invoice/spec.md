## ADDED Requirements

### Requirement: Auto Confirm Invoice company setting
The system SHALL provide a company-level Boolean setting `auto_confirm_invoice` (default `True`) configurable via Rental Settings under the Pickup block. The setting string SHALL be "Auto Confirm Invoice" with help text: "Automatically confirm (post) invoices immediately after creation from a rental order, making them ready for payment."

#### Scenario: Setting is visible in Rental Settings
- **WHEN** a user opens Rental → Configuration → Settings
- **THEN** "Auto Confirm Invoice" checkbox is visible under the Pickup block

#### Scenario: Setting defaults to enabled for new companies
- **WHEN** a new company is created
- **THEN** `auto_confirm_invoice` defaults to `True`

### Requirement: Auto-post rental invoices on creation
When `auto_confirm_invoice` is enabled, the system SHALL automatically post (confirm) all invoices created from rental orders (`is_rental_order = True`) immediately after `_create_invoices()` completes. This includes both the rental invoice and the deposit invoice produced by the deposit-split logic.

#### Scenario: Rental invoice auto-posted when setting is on
- **WHEN** a user creates an invoice from a rental order and `auto_confirm_invoice = True`
- **THEN** the resulting invoice state is `posted` (not `draft`)

#### Scenario: Deposit invoice auto-posted when setting is on
- **WHEN** a rental order with a deposit line generates both a rental invoice and a deposit invoice and `auto_confirm_invoice = True`
- **THEN** both invoices are posted immediately after creation

#### Scenario: Setting off — invoices remain draft
- **WHEN** `auto_confirm_invoice = False` and a user creates an invoice from a rental order
- **THEN** the resulting invoice state is `draft`

### Requirement: Non-rental invoices unaffected
The auto-post logic SHALL NOT affect invoices created from regular sale orders (`is_rental_order = False`), even when processed in the same batch as rental orders.

#### Scenario: Mixed batch — only rental invoices posted
- **WHEN** `_create_invoices()` is called on a mix of rental and non-rental orders with `auto_confirm_invoice = True`
- **THEN** only invoices originating from rental orders are posted; non-rental invoices remain draft

### Requirement: Auto-post failure does not block invoice creation
If `action_post()` fails for an individual invoice (e.g. missing journal or account configuration), the system SHALL log a warning and return the invoice in draft state rather than raising an error that prevents the invoices from being returned.

#### Scenario: Post failure — invoice returned as draft with warning
- **WHEN** `auto_confirm_invoice = True` and `action_post()` raises an exception on a rental invoice
- **THEN** the invoice is returned in draft state, a warning is logged, and no UserError is raised to the user
