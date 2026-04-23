# Test Cases: Reporting & Exports

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- Rental orders in various states (draft, pickup, return, returned)
- Payments and reconciliations in the system
- User with Rental Manager or Supervisor role

---

## 1. Rental Analysis Report (sale.rental.report)

### TC-RP-001: Rental analysis shows orders in "return" state

| Field | Value |
|-------|-------|
| **Precondition** | Order with items picked up |
| **Steps** | 1. Go to Rental > Reports > Rental Analysis |
| **Expected** | Order with `state = return` visible in report |
| **Result** | |

### TC-RP-002: Report expands rental period into daily rows

| Field | Value |
|-------|-------|
| **Precondition** | Rental order for 3 days (May 1–3) |
| **Steps** | 1. View rental analysis report |
| **Expected** | 3 rows for this order (one per day); daily price = total / 3 |
| **Result** | |

### TC-RP-003: qty_delivered normalized by UOM

| Field | Value |
|-------|-------|
| **Precondition** | Order with qty in custom UOM (e.g., "dozen") |
| **Steps** | 1. Check qty_delivered in report |
| **Expected** | Quantity normalized by UOM conversion factor |
| **Result** | |

### TC-RP-004: Report filterable by partner

| Field | Value |
|-------|-------|
| **Precondition** | Orders for multiple customers |
| **Steps** | 1. Filter by specific customer in report |
| **Expected** | Only that customer's orders shown |
| **Result** | |

### TC-RP-005: Report filterable by product category

| Field | Value |
|-------|-------|
| **Precondition** | Products in different categories |
| **Steps** | 1. Filter by category |
| **Expected** | Only products in that category shown |
| **Result** | |

### TC-RP-006: Report filterable by date range

| Field | Value |
|-------|-------|
| **Precondition** | Orders across multiple months |
| **Steps** | 1. Filter by date range May 2026 |
| **Expected** | Only orders active in May shown |
| **Result** | |

### TC-RP-007: Daily price = line subtotal / duration days

| Field | Value |
|-------|-------|
| **Precondition** | Order: 3 days, subtotal = 1,500 |
| **Steps** | 1. Check `price` field in daily report rows |
| **Expected** | Each row shows `price = 500` (1,500 / 3) |
| **Result** | |

---

## 2. Rental Order Report (Print)

### TC-RP-008: Print rental order report

| Field | Value |
|-------|-------|
| **Precondition** | Rental order in any state |
| **Steps** | 1. Click "Print" > Rental Order |
| **Expected** | PDF generated using `rental_order_report_templates.xml` |
| **Result** | |

### TC-RP-009: Print rental contract

| Field | Value |
|-------|-------|
| **Precondition** | Rental order confirmed |
| **Steps** | 1. Click "Print" > Rental Contract |
| **Expected** | PDF generated using `rental_contract_templates.xml` |
| **Result** | |

### TC-RP-010: Rental order report shows correct dates and pricing

| Field | Value |
|-------|-------|
| **Precondition** | Order with start, return dates and pricing |
| **Steps** | 1. Print rental order |
| **Expected** | Dates, product names, quantities, unit prices, and subtotals all correct |
| **Result** | |

---

## 3. Invoice Report

### TC-RP-011: Invoice uses Thai report template

| Field | Value |
|-------|-------|
| **Precondition** | Rental invoice posted |
| **Steps** | 1. Print invoice |
| **Expected** | Template `ggg_rental.ggg_report_invoice_document` used |
| **Result** | |

### TC-RP-012: Thai invoice shows amount in words for THB

| Field | Value |
|-------|-------|
| **Precondition** | Invoice in THB = 12,500 |
| **Steps** | 1. Print invoice |
| **Expected** | Thai words for 12,500 THB displayed on invoice |
| **Result** | |

---

## 4. Reconciliation Period Report Wizard

### TC-RP-013: Open period report wizard

| Field | Value |
|-------|-------|
| **Precondition** | User with supervisor role |
| **Steps** | 1. Go to Rental > Reports > Reconciliation Report<br>2. Open wizard |
| **Expected** | Wizard opens with date_from, date_to defaulting to today |
| **Result** | |

### TC-RP-014: Date range validation — from ≤ to

| Field | Value |
|-------|-------|
| **Precondition** | Period report wizard open |
| **Steps** | 1. Set date_from = 2026-05-10; date_to = 2026-05-01 (from > to) |
| **Expected** | Validation error: date_from must be ≤ date_to |
| **Result** | |

### TC-RP-015: Date range validation — max 90 days

| Field | Value |
|-------|-------|
| **Precondition** | Period report wizard open |
| **Steps** | 1. Set date_from = 2026-01-01; date_to = 2026-05-01 (>90 days) |
| **Expected** | Validation error: range cannot exceed 90 days |
| **Result** | |

### TC-RP-016: Export period report as XLSX

| Field | Value |
|-------|-------|
| **Precondition** | Valid date range set |
| **Steps** | 1. Select format = XLSX<br>2. Click "Generate" |
| **Expected** | XLSX downloaded with columns: Date, Cashier, Expected, Actual, Variance, State |
| **Result** | |

### TC-RP-017: Export period report as PDF

| Field | Value |
|-------|-------|
| **Precondition** | Valid date range |
| **Steps** | 1. Select format = PDF<br>2. Click "Generate" |
| **Expected** | PDF generated and downloaded |
| **Result** | |

### TC-RP-018: Filter period report by cashier

| Field | Value |
|-------|-------|
| **Precondition** | Multiple cashiers with reconciliations |
| **Steps** | 1. Select specific cashier in `cashier_ids`<br>2. Generate XLSX |
| **Expected** | Report shows only selected cashier's reconciliations |
| **Result** | |

### TC-RP-019: Period report includes all cashiers when filter empty

| Field | Value |
|-------|-------|
| **Precondition** | `cashier_ids` = empty |
| **Steps** | 1. Generate report with no cashier filter |
| **Expected** | All cashiers' reconciliations in range included |
| **Result** | |

---

## 5. Single Reconciliation PDF

### TC-RP-020: Print single reconciliation PDF

| Field | Value |
|-------|-------|
| **Precondition** | Reconciliation (draft or confirmed) |
| **Steps** | 1. Open reconciliation record<br>2. Click "Print PDF" |
| **Expected** | PDF using `reconciliation_single_pdf.xml` template generated |
| **Result** | |
