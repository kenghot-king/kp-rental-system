## ADDED Requirements

### Requirement: Customer info section has no visible table borders
In the Thai tax invoice / receipt PDF (ใบเสร็จรับเงิน/ใบกำกับภาษี), the customer information block (Customer Name, Address, Customer Code, Tax Id, No., Date, Term of Payment, Due Date, Vendor Code, Currency) SHALL render without any visible cell borders or table grid lines.

#### Scenario: Thai invoice printed for a customer with full address
- **WHEN** a Thai tax invoice PDF is generated
- **THEN** the customer info area SHALL display as a plain borderless layout — no cell borders, no table grid lines visible

#### Scenario: Layout remains two-column
- **WHEN** borders are removed from the customer info table
- **THEN** the two-column layout (customer left, invoice meta right) SHALL be preserved

---

### Requirement: Payment information section has no visible table borders
The payment/totals block (Total Amount For NON-VAT, Total Amount For VAT, VAT Amount, Grand Total, Withholding Tax, Net Amount) SHALL render without visible cell borders.

#### Scenario: Thai invoice with VAT lines
- **WHEN** the invoice has VAT line items
- **THEN** the totals/payment block SHALL display amounts without visible table borders around cells

#### Scenario: Grand Total and Net Amount separator lines are preserved
- **WHEN** borders are removed from the payment table cells
- **THEN** the `border-top` separator lines above Grand Total and Net Amount rows SHALL still be visible (these are intentional separator lines, not grid borders)
