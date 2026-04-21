## ADDED Requirements

### Requirement: Return creates a proper stock picking

Every rental return processed through the return wizard must produce at least one `stock.picking` of type Receipts (`WH/IN`), with `origin` set to the sale order name.

#### Scenario: Single item returned in good condition
- **WHEN** a return wizard is submitted for one rental line (condition: good)
- **THEN** one `stock.picking` is created (WH/IN sequence), `origin = SO name`, `location_dest_id = WH/Stock`, state = done; the picking contains one `stock.move` linked to it

#### Scenario: Single item returned damaged
- **WHEN** a return wizard is submitted for one rental line (condition: damaged)
- **THEN** one `stock.picking` is created, `origin = SO name`, `location_dest_id = WH/Damage`, state = done

#### Scenario: Single item sent to inspection
- **WHEN** a return wizard is submitted for one rental line (condition: inspect)
- **THEN** one `stock.picking` is created, `origin = SO name`, `location_dest_id = WH/Inspection`, state = done

### Requirement: Same-destination lines share one picking per return event

When multiple rental lines in the same return wizard submit go to the same destination location, they are grouped under a single picking.

#### Scenario: Two items returned good in one wizard submit
- **WHEN** a return wizard is submitted with two lines both in good condition
- **THEN** exactly one `stock.picking` is created (not two), containing two `stock.move` records, both linked to that picking

### Requirement: Different-destination lines get separate pickings

When lines in the same return wizard submit go to different destinations, each destination gets its own picking.

#### Scenario: Mixed conditions in one wizard submit
- **WHEN** a return wizard is submitted with one line in good condition and one line damaged
- **THEN** two `stock.picking` records are created: one to WH/Stock, one to WH/Damage; each contains its respective move

### Requirement: SO number stamped as Source Document

Both the `stock.picking.origin` and `stock.move.origin` must equal the sale order name (e.g., `S00259`).

#### Scenario: Warehouse staff traces return to SO
- **WHEN** a warehouse user filters Inventory → Transfers by Source Document = "S00259"
- **THEN** the return picking(s) for S00259 appear in the results

### Requirement: Delivery pickings (pickup) are unaffected

The existing pickup flow (stock rules → WH/OUT delivery orders) must continue to work exactly as before.

#### Scenario: Pickup flow unchanged
- **WHEN** a rental order is confirmed and pickup is processed
- **THEN** the delivery order (WH/OUT) is created and validated exactly as before, with no change in behavior
