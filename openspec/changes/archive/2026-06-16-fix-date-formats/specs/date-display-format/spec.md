## ADDED Requirements

### Requirement: Rental order line description uses dd/MM/yyyy HH:mm format
The system SHALL render the rental period description on sale order lines using `dd/MM/yyyy, HH:mm` for full datetime ranges and `HH:mm` for the return time when pickup and return fall on the same calendar day, regardless of the user's Odoo language setting.

#### Scenario: Multi-day rental period
- **WHEN** a rental order line has `rental_start_date` = 2026-04-30 09:00 and `rental_return_date` = 2026-05-01 23:59
- **THEN** the line description shows `\n30/04/2026, 09:00 to 01/05/2026, 23:59`

#### Scenario: Same-day rental (return on same date as pickup)
- **WHEN** a rental order line has `rental_start_date` = 2026-04-30 09:00 and `rental_return_date` = 2026-04-30 18:00
- **THEN** the line description shows `\n30/04/2026, 09:00 to 18:00`

#### Scenario: Format is locale-independent
- **WHEN** the logged-in user's Odoo language is `en_US`
- **THEN** the rental period description still displays `dd/MM/yyyy` date format (not `M/D/YY`)

### Requirement: Rental order report displays dates in dd/MM/yyyy HH:mm format
The rental order report (printed PDF) SHALL display `line.start_date` and `line.return_date` columns in `dd/MM/yyyy HH:mm` format.

#### Scenario: Pickup date column in rental order report
- **WHEN** a rental order PDF is generated
- **THEN** the Pickup Date column shows dates as `dd/MM/yyyy HH:mm` (e.g. `30/04/2026 09:00`)

#### Scenario: Expected Return column in rental order report
- **WHEN** a rental order PDF is generated
- **THEN** the Expected Return column shows dates as `dd/MM/yyyy HH:mm`

### Requirement: Thai tax invoice displays dates in dd/MM/yyyy format
The Thai tax invoice PDF SHALL display `invoice_date` and `invoice_date_due` in `dd/MM/yyyy` format.

#### Scenario: Invoice date on Thai tax invoice
- **WHEN** a Thai tax invoice PDF is generated
- **THEN** the invoice date field shows `dd/MM/yyyy` (e.g. `29/04/2026`)

#### Scenario: Due date on Thai tax invoice
- **WHEN** a Thai tax invoice PDF is generated
- **THEN** the due date field shows `dd/MM/yyyy`

### Requirement: Rental contract displays dates in dd/MM/yyyy format
The rental contract PDF SHALL display all date fields — the header document date (`rental_start_date` in the วันที่ block) and the rental period table (`rental_start_date` / `rental_return_date`) — in `dd/MM/yyyy` format.

#### Scenario: Header document date on contract
- **WHEN** a rental contract PDF is generated
- **THEN** the วันที่ field shows `dd/MM/yyyy` (e.g. `30/04/2026`)

#### Scenario: Rental period table dates on contract
- **WHEN** a rental contract PDF is generated
- **THEN** both the start-date and return-date cells in the period table show `dd/MM/yyyy`
