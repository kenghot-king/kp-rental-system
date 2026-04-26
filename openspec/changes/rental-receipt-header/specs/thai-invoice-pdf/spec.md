## MODIFIED Requirements

### Requirement: Bilingual title block
The template SHALL display a centered, bold title block whose Thai text depends on the move type and VAT content of the document. The title SHALL be Thai-only (no English subtitle). The title SHALL be determined as follows:

- If `o.move_type == 'out_refund'`, the title SHALL be `"ใบลดหนี้"`.
- Else if any product line in `o.invoice_line_ids` (where `display_type == 'product'`) has at least one tax with `amount > 0`, the title SHALL be `"ใบเสร็จรับเงิน/ใบกำกับภาษี"`.
- Otherwise the title SHALL be `"ใบเสร็จรับเงิน"`.

VAT 0% taxes and withholding taxes (negative `amount`) SHALL NOT trigger the combined Receipt/Tax Invoice title.

#### Scenario: Paid invoice with at least one VAT line renders combined title
- **WHEN** a paid `out_invoice` has at least one product line carrying a tax with `amount > 0`
- **THEN** the title block SHALL display `"ใบเสร็จรับเงิน/ใบกำกับภาษี"` and SHALL NOT display any English subtitle

#### Scenario: Paid invoice with no VAT line renders plain receipt title
- **WHEN** a paid `out_invoice` has no product line carrying a tax with `amount > 0`
- **THEN** the title block SHALL display `"ใบเสร็จรับเงิน"`

#### Scenario: VAT 0% is treated as no-VAT
- **WHEN** a paid `out_invoice` has product lines whose only taxes are 0% VAT (amount equals 0)
- **THEN** the title block SHALL display `"ใบเสร็จรับเงิน"`

#### Scenario: Credit note renders ใบลดหนี้
- **WHEN** an `out_refund` is printed
- **THEN** the title block SHALL display `"ใบลดหนี้"` regardless of VAT content

#### Scenario: Withholding tax alone does not trigger combined title
- **WHEN** a paid `out_invoice` has only taxes with `amount < 0` (withholding)
- **THEN** the title block SHALL display `"ใบเสร็จรับเงิน"`

## ADDED Requirements

### Requirement: Print gated on payment_state for out_invoice
The system SHALL block PDF rendering of any `out_invoice` whose `payment_state` is not `"paid"`. The block SHALL be enforced in `account.move._get_name_invoice_report()` by raising `odoo.exceptions.UserError` with the message `"ไม่สามารถพิมพ์ใบเสร็จได้ เนื่องจากยังไม่ชำระเงิน"`. The gate SHALL apply to every render path: the toolbar print button, the cog-menu report binding, direct URL access to `/report/pdf/...`, the email preview, and any other call that resolves the invoice report template name.

The gate SHALL NOT apply to `out_refund` — credit notes SHALL be printable regardless of `payment_state`.

The gate SHALL treat `payment_state` values other than `"paid"` — including `"not_paid"`, `"in_payment"`, `"partial"`, `"reversed"`, and any other state — as unprintable.

#### Scenario: Unpaid invoice print is blocked
- **WHEN** a user attempts to print an `out_invoice` with `payment_state == 'not_paid'` by any path (button, cog menu, direct URL, email)
- **THEN** the system SHALL raise `UserError` with the message `"ไม่สามารถพิมพ์ใบเสร็จได้ เนื่องจากยังไม่ชำระเงิน"` and SHALL NOT produce a PDF

#### Scenario: In-payment invoice print is blocked
- **WHEN** a user attempts to print an `out_invoice` with `payment_state == 'in_payment'`
- **THEN** the system SHALL raise `UserError` and SHALL NOT produce a PDF

#### Scenario: Partially paid invoice print is blocked
- **WHEN** a user attempts to print an `out_invoice` with `payment_state == 'partial'`
- **THEN** the system SHALL raise `UserError` and SHALL NOT produce a PDF

#### Scenario: Paid invoice prints successfully
- **WHEN** a user prints an `out_invoice` with `payment_state == 'paid'`
- **THEN** the system SHALL render the PDF using `ggg_rental.ggg_report_invoice_document` without raising an error

#### Scenario: Credit note prints regardless of payment_state
- **WHEN** a user prints an `out_refund` with any `payment_state` value
- **THEN** the system SHALL render the PDF without raising an error
