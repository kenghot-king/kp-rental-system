## ADDED Requirements

### Requirement: deposit_price included in product CSV template
The template downloaded from `/ggg_rental/download_product_template` SHALL include a `deposit_price` column. On import, a non-empty value SHALL be written to `product.template.deposit_price` as a Float. An empty cell SHALL be skipped (field left unchanged).

#### Scenario: Template download includes deposit_price column
- **WHEN** a user downloads the product template
- **THEN** the CSV headers include `deposit_price` positioned after `extra_daily`

#### Scenario: Import sets deposit_price from non-empty value
- **WHEN** a CSV row contains `deposit_price = 5000`
- **THEN** the product's `deposit_price` is set to `5000.0`

#### Scenario: Import skips empty deposit_price
- **WHEN** a CSV row contains an empty `deposit_price` cell
- **THEN** the product's existing `deposit_price` is unchanged

### Requirement: sale_ok included in product CSV template
The template SHALL include a `sale_ok` column. On import, accepted truthy values (`true`, `1`, `yes`) SHALL set `sale_ok = True`; any other non-empty value SHALL set `sale_ok = False`. An empty cell SHALL be skipped.

#### Scenario: Template download includes sale_ok column
- **WHEN** a user downloads the product template
- **THEN** the CSV headers include `sale_ok`

#### Scenario: Import sets sale_ok true
- **WHEN** a CSV row contains `sale_ok = True`
- **THEN** the product's `sale_ok` is set to `True`

#### Scenario: Import skips empty sale_ok
- **WHEN** a CSV row contains an empty `sale_ok` cell
- **THEN** the product's existing `sale_ok` is unchanged

### Requirement: taxes_id included in product CSV template
The template SHALL include a `taxes_id` column containing semicolon-separated sales tax names. On import, each name SHALL be resolved against `account.tax` (filtered `type_tax_use = sale`) by exact name match. Successfully resolved taxes SHALL replace the product's `taxes_id`. Unresolved names SHALL be added to the import warnings and skipped. An empty cell SHALL be skipped (taxes left unchanged).

#### Scenario: Template download includes taxes_id column
- **WHEN** a user downloads the product template
- **THEN** the CSV headers include `taxes_id` and the example row contains a representative tax name

#### Scenario: Import sets single tax by name
- **WHEN** a CSV row contains `taxes_id = Output 7% include`
- **THEN** the product's `taxes_id` is set to the matching `account.tax` record

#### Scenario: Import sets multiple taxes semicolon-separated
- **WHEN** a CSV row contains `taxes_id = Tax A;Tax B`
- **THEN** the product's `taxes_id` is set to both resolved tax records

#### Scenario: Import warns on unresolved tax name
- **WHEN** a CSV row contains `taxes_id = NonExistentTax`
- **THEN** a warning is added to the import result and the product's `taxes_id` is unchanged

#### Scenario: Import skips empty taxes_id
- **WHEN** a CSV row contains an empty `taxes_id` cell
- **THEN** the product's existing `taxes_id` is unchanged
