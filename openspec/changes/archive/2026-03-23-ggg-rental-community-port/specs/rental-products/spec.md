## ADDED Requirements

### Requirement: Rental product toggle
The system SHALL add a `rent_ok` boolean field to `product.template` (default: context-based via `in_rental_app`) that marks a product as available for rental.

#### Scenario: Enable rental on product
- **WHEN** a user checks the "Rental" checkbox on a product form
- **THEN** `rent_ok=True` and the "Rental Prices" tab becomes visible

#### Scenario: Product created in rental app
- **WHEN** a product is created from the Rental app context
- **THEN** `rent_ok` defaults to TRUE

### Requirement: Product pricing rules
The system SHALL add `product_pricing_ids` (one2many to `product.pricing`) on `product.template`, allowing multiple pricing rules to be defined per product with different recurrences and pricelists.

#### Scenario: Add pricing rule to product
- **WHEN** a user adds a pricing rule with recurrence "Daily" at $50
- **THEN** the rule appears in the product's "Rental Prices" tab

#### Scenario: Display price computation
- **WHEN** a product has pricing rules
- **THEN** `display_price` shows the first rule's description (e.g., "$50.00 / Day")

#### Scenario: No pricing rules
- **WHEN** a rental product has no pricing rules
- **THEN** `display_price` falls back to the product's list price

### Requirement: Quantity in rent tracking
The system SHALL compute `qty_in_rent` on both `product.template` and `product.product` as the sum of `(qty_delivered - qty_returned)` across confirmed rental order lines.

#### Scenario: Active rental tracked
- **WHEN** a rental order has 3 bikes picked up and 1 returned
- **THEN** the Bike product shows `qty_in_rent = 2`

#### Scenario: Only confirmed orders counted
- **WHEN** a rental order is in draft/quotation state
- **THEN** its lines do not contribute to `qty_in_rent`

### Requirement: Late fee fields on product
The system SHALL add `extra_hourly` (monetary) and `extra_daily` (monetary) fields to `product.template`, company-dependent, with defaults set via `ir.default` from company configuration.

#### Scenario: Set late fees per product
- **WHEN** a product's `extra_hourly` is set to $10 and `extra_daily` to $50
- **THEN** late returns of this product are charged at those rates

#### Scenario: Default from company settings
- **WHEN** a new rental product is created
- **THEN** `extra_hourly` and `extra_daily` inherit from `ir.default` values set in configuration

### Requirement: Delay price calculation
The system SHALL provide `_compute_delay_price(timedelta)` on `product.product` that returns `days × extra_daily + hours × extra_hourly`.

#### Scenario: Calculate delay price
- **WHEN** a product has `extra_daily=50`, `extra_hourly=10`, and the delay is 2 days 3 hours
- **THEN** delay price = 2×50 + 3×10 = $130

### Requirement: Rental combo product constraint
The system SHALL enforce that combo products containing rental items can ONLY contain rental sub-products (all or none).

#### Scenario: Mixed combo rejected
- **WHEN** a combo product with `rent_ok=True` includes a sub-product with `rent_ok=False`
- **THEN** the system raises a validation error

### Requirement: Rental product views
The system SHALL provide product template form/tree/kanban views with: "Rental" toggle in sales section, "Rental Prices" tab (editable pricing rules table), reservations section (extra_hourly, extra_daily), "In Rental" stat button linking to Gantt schedule, and tree/kanban views showing rental pricing instead of list price for rental products.

#### Scenario: Product form rental tab
- **WHEN** `rent_ok=True` on a product
- **THEN** the form shows a "Rental Prices" tab with columns: Recurrence, Pricelist, Price, Variants

#### Scenario: In Rental stat button
- **WHEN** a product has `qty_in_rent > 0`
- **THEN** clicking the "In Rental" stat button opens the rental schedule Gantt view filtered to that product

### Requirement: Pricelist rental pricing tab
The system SHALL add `product_pricing_ids` (one2many) to `product.pricelist` and enforce that all pricing rules reference rent_ok products.

#### Scenario: Pricelist pricing rules
- **WHEN** viewing a pricelist form
- **THEN** a "Rental Pricing" section shows pricing rules specific to that pricelist

#### Scenario: Non-rental product rejected
- **WHEN** a pricing rule references a product with `rent_ok=False`
- **THEN** the system raises a validation error

### Requirement: Best pricing rule selection on product
The system SHALL provide `_get_best_pricing_rule(start_date, end_date, pricelist, currency)` on `product.template` that evaluates all applicable pricing rules and returns the one with the minimum total cost.

#### Scenario: Best rule selected
- **WHEN** a product has Daily ($50), Weekly ($300), Monthly ($1000) pricing and the rental is 10 days
- **THEN** the method evaluates all three rules and returns the one producing the lowest total
