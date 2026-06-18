## MODIFIED Requirements

### Requirement: Quotation total row label
The sale order / quotation PDF total row SHALL display "ยอดรวม" as the Thai label, replacing Odoo's default base translation "ทั้งหมด" of `msgid "Total"`.

#### Scenario: Quotation total label in Thai
- **WHEN** a quotation PDF is rendered with `lang=th_TH`
- **THEN** the o_total row's first column SHALL display "ยอดรวม"

#### Scenario: Override mechanism
- **WHEN** the ggg_rental module is installed or upgraded
- **THEN** its `i18n/th.po` SHALL re-translate `msgid "Total"` to `msgstr "ยอดรวม"` so it takes precedence over base translations rendered by reports loaded with this module

## ADDED Requirements

### Requirement: Rental contract "รวม" column displays VAT-included amount
The rental contract PDF "รวม" column for rental items SHALL display each line's `price_total` (VAT-included), not `price_subtotal`.

#### Scenario: Single rental line with 7% VAT
- **WHEN** a rental order has a line with unit price 1,486.92 and tax-excluded VAT 7%
- **THEN** the contract "รวม" column for that line SHALL display "1,591.01" (= 1,486.92 × 1.07, formatted with two decimals)

#### Scenario: Tax-included pricing
- **WHEN** a rental order has a line where `price_unit` already includes VAT
- **THEN** the contract "รวม" column SHALL still display `price_total`, which Odoo computes correctly for tax-included pricing

#### Scenario: Deposit table unaffected
- **WHEN** a rental order contains deposit lines
- **THEN** the deposit table "รวม" column SHALL continue to display `price_subtotal` (which equals `price_total` for zero-tax deposits)

### Requirement: Rental contract financial summary itemizes tax by tax group
The rental contract financial summary SHALL replace the single bare "ภาษี" row with one row per tax group present on the order, each row labeled with the tax group's `group_name` and showing its `tax_amount_currency`.

#### Scenario: Single VAT 7% group
- **WHEN** a rental order has all taxed lines using one tax group named "ภาษีมูลค่าเพิ่ม 7%"
- **THEN** the financial summary SHALL render exactly one tax row labeled "ภาษีมูลค่าเพิ่ม 7%" with the corresponding tax amount

#### Scenario: Multiple tax groups
- **WHEN** a rental order has lines using two or more distinct tax groups
- **THEN** the financial summary SHALL render one row per tax group, each labeled with its `group_name` and showing its `tax_amount_currency`

#### Scenario: No taxed lines
- **WHEN** a rental order has zero tax (`doc.amount_tax == 0`)
- **THEN** the financial summary SHALL render no tax group rows

#### Scenario: Data source
- **WHEN** the financial summary renders tax rows
- **THEN** it SHALL iterate `doc.tax_totals['subtotals'][*]['tax_groups'][*]` (the same data structure used by the quotation PDF) — no separate per-line tax computation

### Requirement: Rental contract financial summary reconciles to per-line column
The rental contract financial summary SHALL include both an incl-VAT rental subtotal that reconciles to the rental items column sum and an ex-VAT rental subtotal that combines with the tax group rows and deposit to reach the grand total.

#### Scenario: Incl-VAT subtotal matches column
- **WHEN** the contract is rendered with rental lines whose `price_total` values sum to N
- **THEN** the financial summary SHALL include a row "ยอดรวมค่าเช่า (รวมภาษี)" with value N

#### Scenario: Ex-VAT subtotal plus tax groups plus deposit equals grand total
- **WHEN** the contract is rendered
- **THEN** "ยอดรวมค่าเช่า (ไม่รวมภาษี)" + Σ(tax group amounts) + "เงินประกัน" SHALL equal "ยอดรวมทั้งสิ้น"

#### Scenario: Ordering of rows
- **WHEN** the financial summary renders
- **THEN** the row order SHALL be: ยอดรวมค่าเช่า (รวมภาษี), เงินประกัน, ยอดรวมค่าเช่า (ไม่รวมภาษี), tax group rows, ยอดรวมทั้งสิ้น
