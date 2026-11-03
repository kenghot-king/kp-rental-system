# rental-invoice-by-item-report Specification

## Purpose
Lets accounting check customer invoices and their reverse invoices (credit notes) line by line in the Rental By Item report, with net totals and a trace back to the order and original invoice.
## Requirements
### Requirement: Report includes invoices and credit notes

The By Item report SHALL list the product lines of customer invoices and customer credit notes. It SHALL NOT list other journal items, such as tax or receivable lines, or lines from vendor documents.

#### Scenario: Credit note appears in the report
- **WHEN** a posted customer credit note (RINV) exists
- **THEN** each of its product lines SHALL appear in the report

#### Scenario: Other journal items stay excluded
- **WHEN** a posted customer invoice has tax and receivable journal items and a posted vendor bill exists
- **THEN** the report SHALL list only the invoice's product lines

### Requirement: Credit note amounts reduce totals

The report SHALL show Subtotal and Tax as negative on credit note lines and as positive on invoice lines, so that column totals and group totals are net. Unit Price and Quantity SHALL remain positive on both.

#### Scenario: Full credit note nets to zero
- **WHEN** an invoice with Subtotal 300.00 and Tax 21.00 is fully credited
- **THEN** the credit note line SHALL show Subtotal -300.00 and Tax -21.00, and the totals for the two documents SHALL be 0.00

#### Scenario: Partial credit note nets to the remainder
- **WHEN** an invoice with Subtotal 300.00 has a posted credit note for 100.00
- **THEN** the Subtotal total for the two documents SHALL be 200.00

#### Scenario: Grouped totals are net
- **WHEN** the report is grouped by Order and the order has an invoice and a credit note
- **THEN** the group's Subtotal and Tax totals SHALL be net of the credit note

#### Scenario: Unit Price and Quantity stay as printed
- **WHEN** a credit note line has quantity 1 and unit price 300.00
- **THEN** the report SHALL show Quantity 1 and Unit Price 300.00

### Requirement: Lines trace to their order

The report SHALL show the sale order for each line, and SHALL allow searching and grouping by it. This SHALL work however the credit note was created. A line with no linked sale order SHALL still appear, with the Order value empty.

#### Scenario: Automatic deposit refund shows the order
- **WHEN** a cash-paid deposit is refunded on return and a credit note is created automatically
- **THEN** the credit note line SHALL show the rental order

#### Scenario: Manual credit note shows the order
- **WHEN** a user creates a credit note from an invoice linked to a sale order
- **THEN** the credit note lines SHALL show the same order as the original invoice lines

#### Scenario: Invoice and reversal group together
- **WHEN** the report is grouped by Order
- **THEN** an invoice and its credit note for that order SHALL appear in the same group

#### Scenario: Document with no sale order
- **WHEN** a customer invoice or credit note has no link to a sale order
- **THEN** its lines SHALL appear with an empty Order value

### Requirement: Credit notes show the original invoice

The report SHALL show the original invoice on credit note lines that reverse an invoice. The value SHALL be empty on invoice lines and on credit notes with no original invoice.

#### Scenario: Reversal shows its original invoice
- **WHEN** a credit note reverses an invoice
- **THEN** its lines SHALL show that invoice as Reversal Of

#### Scenario: Invoice has no reversal value
- **WHEN** a line belongs to an invoice, even one that has been credited
- **THEN** its Reversal Of value SHALL be empty

### Requirement: Document type and payment status can be filtered

The report SHALL offer filters for Invoices, Credit Notes and the Reversed payment status, and SHALL show the Reversed status in a colour distinct from the other payment statuses. These new filters SHALL NOT be added to other journal item screens.

#### Scenario: Show credit notes only
- **WHEN** the user applies the Credit Notes filter
- **THEN** only credit note lines SHALL be listed

#### Scenario: Show reversed invoices
- **WHEN** an unpaid invoice has been fully credited and the user applies the Reversed filter
- **THEN** that invoice's lines SHALL be listed with a Reversed status badge

#### Scenario: Other screens are unaffected
- **WHEN** a user opens another journal items screen
- **THEN** the Invoices, Credit Notes and Reversed filters SHALL NOT be offered

### Requirement: Report defaults to posted documents

The report SHALL open showing posted documents only. Users SHALL be able to remove this filter to see draft and cancelled documents, whose lines SHALL then count towards totals.

#### Scenario: Draft and cancelled documents hidden on open
- **WHEN** a draft credit note and a cancelled credit note exist and the user opens the report
- **THEN** their lines SHALL NOT be listed or counted in totals

#### Scenario: Removing the filter shows all documents
- **WHEN** the user removes the Posted filter
- **THEN** lines from draft and cancelled documents SHALL be listed with their status

### Requirement: Report does not change financial data

The report SHALL be read-only. Users SHALL NOT be able to create, edit or delete lines from it, and showing credit notes SHALL NOT change any document, payment or stored accounting amount. It SHALL NOT imply a credit note exists where none was issued.

#### Scenario: Lines cannot be changed from the report
- **WHEN** a user opens the report
- **THEN** creating, editing and deleting lines SHALL NOT be available

#### Scenario: Stored amounts are unchanged
- **WHEN** the module is upgraded on a database with posted invoices and credit notes
- **THEN** the debit, credit, balance, unit price and untaxed amount of existing journal items SHALL be unchanged

#### Scenario: Held deposit has no credit note line
- **WHEN** a held deposit is released or forfeited and the item is returned
- **THEN** the report SHALL show no credit note line for that deposit

