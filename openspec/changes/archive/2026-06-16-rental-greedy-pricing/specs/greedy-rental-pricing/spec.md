## ADDED Requirements

### Requirement: Greedy period decomposition for rental pricing
The system SHALL compute the rental price by greedily decomposing the total rental duration into the largest available pricing periods first, accumulating costs across all tiers, rather than selecting a single rule repeated for the entire duration.

The algorithm SHALL:
1. Collect all applicable `product.pricing` rules for the product/pricelist, normalized to days
2. Sort rules by period length descending (largest first)
3. For each rule except the smallest: apply `floor(remaining_days / period_days)` repetitions; subtract consumed days from the remainder
4. For the smallest rule: apply `ceil(remaining_days / period_days)` to cover any leftover (minimum 1 if remainder > 0)
5. Return the sum of all contributions

#### Scenario: Multi-tier decomposition
- **WHEN** a product has pricing [12d @ 500฿, 7d @ 300฿, 1d @ 50฿] and is rented for 22 days
- **THEN** the system computes: 1×500 + 1×300 + 3×50 = 950฿

#### Scenario: Exact period boundary
- **WHEN** a product has pricing [7d @ 300฿, 1d @ 50฿] and is rented for 7 days
- **THEN** the system computes: 1×300 = 300฿ (no remainder)

#### Scenario: No daily rate — remainder charged at smallest period
- **WHEN** a product has pricing [12d @ 500฿, 7d @ 300฿] (no daily) and is rented for 22 days
- **THEN** the system computes: 1×500 + ceil(10/7)×300 = 500 + 2×300 = 1,100฿

#### Scenario: Single pricing rule
- **WHEN** a product has only one pricing rule [1d @ 50฿] and is rented for 9 days
- **THEN** the system computes: ceil(9/1)×50 = 450฿

#### Scenario: Greedy produces lower price than single-rule selection
- **WHEN** a product has pricing [12d @ 500฿, 1d @ 50฿] and is rented for 22 days
- **THEN** greedy gives 1×500 + 10×50 = 1,000฿ (same as old single-rule for this case, no regression)

### Requirement: Period normalization to days
The system SHALL normalize all pricing periods to a common unit (days) before sorting and decomposition, using the existing PERIOD_RATIO constants (hour=1, day=24, week=168).

#### Scenario: Weekly period treated as 7 days
- **WHEN** a pricing rule has recurrence `duration=1, unit='week'`
- **THEN** the system treats it as 7 days during decomposition

#### Scenario: Custom day-count period
- **WHEN** a pricing rule has recurrence `duration=12, unit='day'`
- **THEN** the system treats it as 12 days during decomposition
