## ADDED Requirements

### Requirement: No duplicate deposit invoice after credit note

A deposit sale order line that already has at least one posted `out_invoice` linked via `invoice_lines` must not be included in the set of invoiceable lines when `_create_invoices()` is called.

#### Scenario: Late-fee invoice created after deposit refund
- **WHEN** a rental return is processed, the deposit credit note is auto-created (linked to the deposit SO line), and the user then creates an invoice for the late-return fee
- **THEN** only the late-return fee invoice is created; no new deposit invoice is generated

#### Scenario: Manual invoice creation after full deposit refund
- **WHEN** the deposit has been invoiced and fully refunded (credit note = original invoice amount) and the user manually triggers "Create Invoice"
- **THEN** no deposit invoice is created (deposit line is excluded from invoiceable lines)

#### Scenario: Partial return — deposit partially credited
- **WHEN** only some items have been returned (partial deposit credit note issued) and an invoice is created for remaining charges
- **THEN** no new deposit invoice is created; the deposit line is excluded because a posted invoice already exists for it

#### Scenario: Cancelled deposit invoice allows re-invoicing
- **WHEN** the original deposit invoice has been cancelled (state = `cancel`) and a new invoice is created
- **THEN** the deposit line IS included (no posted invoice exists), allowing a fresh deposit invoice to be created

### Requirement: Split path not triggered for already-invoiced deposits

The `needs_split` check inside `_create_invoices()` must exclude deposit lines that already have a posted invoice when evaluating whether a deposit/non-deposit split is needed.

#### Scenario: Delay fee invoice on order with refunded deposit
- **WHEN** the delay fee line has `qty_to_invoice > 0` and the deposit line has `qty_to_invoice > 0` (due to credit note) but the deposit was already invoiced
- **THEN** `needs_split` is `False` (or split produces empty deposit batch), and only one invoice is created for the delay fee
