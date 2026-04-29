## ADDED Requirements

### Requirement: Quotation PDF omits Terms and Conditions block
The sale order quotation PDF (ใบเสนอราคา) SHALL NOT render the Terms & Conditions URL or note block. No "เงื่อนไขและข้อกำหนด" heading, URL, or link SHALL appear anywhere on the printed quotation.

#### Scenario: Quotation with T&C URL configured on company
- **WHEN** the company has a T&C URL set and a quotation PDF is printed
- **THEN** the PDF SHALL NOT show the T&C URL or its label

#### Scenario: Quotation with note field populated
- **WHEN** the sale order has a `note` field with T&C or any text
- **THEN** that note SHALL NOT appear in the quotation PDF output

#### Scenario: Quotation content is otherwise unchanged
- **WHEN** the T&C block is suppressed
- **THEN** all other quotation content (line items, totals, customer info, salesperson) SHALL render normally
