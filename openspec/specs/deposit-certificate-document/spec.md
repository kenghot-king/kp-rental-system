## ADDED Requirements

### Requirement: Deposit Certificate document

The system SHALL provide a printable **ใบมัดจำ (Deposit Certificate)** PDF for a deposit invoice,
based on the Thai invoice/receipt layout but with deposit-specific presentation.

#### Scenario: Title shows ใบมัดจำ
- **WHEN** the Deposit Certificate is rendered for a deposit invoice
- **THEN** the document title SHALL read "ใบมัดจำ" instead of "ใบเสร็จรับเงิน/ใบกำกับภาษี"

#### Scenario: No signature block
- **WHEN** the Deposit Certificate is rendered
- **THEN** the bottom "Received by / Authorized Signature" block SHALL be omitted

#### Scenario: Number shows the Sale Order number
- **WHEN** the Deposit Certificate is rendered for a deposit invoice linked to a Sale Order
- **THEN** the "No." field SHALL display the Sale Order number rather than the invoice number

#### Scenario: File name uses the Sale Order number
- **WHEN** the Deposit Certificate PDF is downloaded
- **THEN** the file name SHALL be `Deposit Certificate-{SO no.}.pdf`
