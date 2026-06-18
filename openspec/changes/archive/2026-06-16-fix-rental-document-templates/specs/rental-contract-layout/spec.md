## ADDED Requirements

### Requirement: Equal-height lessor and lessee boxes
The rental contract PDF SHALL render the ผู้ให้เช่า (lessor) and ผู้เช่า (lessee) information boxes at equal height, regardless of how many address lines each party has.

#### Scenario: Lessee has fewer address lines than lessor
- **WHEN** the lessee contact has only name, phone, and email (no street/city)
- **THEN** the lessee box SHALL extend to the same height as the lessor box

#### Scenario: Both parties have equal address length
- **WHEN** both lessor and lessee have the same number of contact lines
- **THEN** both boxes SHALL render at the same height with no visual gap

---

### Requirement: Contract document date equals rental start date
The "วันที่" field in the top-right header of the rental contract SHALL display the rental pickup/start date (`rental_start_date`), formatted as `dd/MM/yyyy`.

#### Scenario: Contract printed after order creation
- **WHEN** a rental contract PDF is generated for an order where `date_order` ≠ `rental_start_date`
- **THEN** the document date SHALL show `rental_start_date` in `dd/MM/yyyy` format, not `date_order`

#### Scenario: Date format
- **WHEN** the rental start date is 27 April 2026 at 09:00
- **THEN** the document date SHALL display as `27/04/2026` (date only, no time component)

---

### Requirement: Company header does not overlap body content on subsequent pages
On rental contract PDFs that span more than one page, the company address running header SHALL NOT overlap the body text on pages 2 and beyond.

#### Scenario: Multi-page contract with long T&C
- **WHEN** the rental contract terms and conditions cause content to overflow to page 2
- **THEN** body text on page 2 SHALL start below the company header, with no visual overlap

#### Scenario: Three-page contract
- **WHEN** content overflows to a third page
- **THEN** body text on page 3 SHALL also start below the company header

---

### Requirement: Signature section starts on its own page
The "การรับทราบและยืนยัน" (acknowledgement and signature) section of the rental contract SHALL always begin on a new page, regardless of how much content precedes it.

#### Scenario: Short T&C — signature on same page as T&C
- **WHEN** the terms block is short enough to leave room on the same page
- **THEN** the signature section SHALL still be forced onto the next page

#### Scenario: Long T&C — signature naturally on next page
- **WHEN** the terms block already pushes content past the page boundary
- **THEN** the signature section SHALL appear at the top of the following page
