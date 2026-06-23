## ADDED Requirements

### Requirement: Receipt date reflects the paid date

The ใบเสร็จรับเงิน/ใบกำกับภาษี "Date" SHALL show the date the invoice was paid (the reconciled
payment's date), not the invoice date. This assumes no partial payments — one invoice is settled by
a single payment.

#### Scenario: Receipt shows the payment date
- **WHEN** a paid invoice's receipt is printed
- **THEN** the "Date" field SHALL show the date of the payment reconciled against that invoice

#### Scenario: No reconciled payment falls back to invoice date
- **WHEN** the receipt is rendered and no reconciled payment can be found
- **THEN** the "Date" field SHALL fall back to the invoice date

### Requirement: Forfeit receipt shows the forfeiture date

Forfeiting a deposit SHALL date the captured hold payment to the chosen forfeiture date, so that the
forfeit receipt's paid date equals the forfeiture date without modifying the posted invoice's
invoice date.

#### Scenario: Forfeiture date drives the receipt date
- **WHEN** a deposit hold is forfeited with a chosen forfeiture date and the receipt is printed
- **THEN** the receipt "Date" SHALL equal the forfeiture date

#### Scenario: Posted invoice date is unchanged by forfeit
- **WHEN** a deposit hold is forfeited
- **THEN** the deposit invoice's `invoice_date` SHALL remain unchanged
