## Context

The `ggg_rental` module already integrates stock via the `sale_stock` dependency. For serial-tracked products, individual units are represented as `stock.lot` records, and their physical location is tracked by `stock.quant` records (one per lot/location pair, qty = 1.0 for serials).

The existing rental product CSV import (`controllers/rental_csv.py`) established a working pattern: a controller with `download_*_template` and `import_*` endpoints, JSON result reporting, and toolbar buttons on the rental product list view. This change extends that pattern to serial number / initial stock loading.

The accounting chosen path: Odoo is the system of record for fleet valuation. The import uses Odoo's standard inventory adjustment mechanism (`stock.quant._apply_inventory()`), which books the fleet to *Stock Valuation* against the *Inventory Adjustment* account at each product's `standard_price`. The user must set product cost before importing, and the accountant records a one-time journal entry to retire any prior fleet asset row in the books.

## Goals / Non-Goals

**Goals:**
- Bulk-create `stock.lot` records for serial-tracked rental products from a CSV
- Land each serial at the active company's default warehouse `lot_stock_id` (WH/Stock) with quantity 1.0
- Use `sap_article_code` as the product match key (consistent with product import)
- Warn-and-continue on duplicate serials so a partial CSV doesn't abort the whole import
- Use Odoo's standard accounting flow so the import is valuation-correct

**Non-Goals:**
- Importing stock for non-serial-tracked products (consumables, services, lot-tracked) — out of scope
- Importing serials to locations other than WH/Stock (Damage, Inspection, Rental) — out of scope; those flows go through the return wizard or standard Odoo transfers
- Setting `standard_price` from the CSV — cost is governed by product master data
- Updating or deleting existing serials — import-only (not an upsert)
- Multi-warehouse selection — uses the active company's default warehouse only

## Decisions

### 1. Two-column template (sap_article_code + serial_number)

```
sap_article_code, serial_number
FORK-001,         SN-2026-001
FORK-001,         SN-2026-002
DRILL-A,          DRL-X-001
```

**Why:** Destination is always WH/Stock (per the accepted scope), quantity is always 1.0 for serials, and product cost lives on the product master. There is nothing else to vary per row.

### 2. WH/Stock = active company's default warehouse `lot_stock_id`

The destination is resolved at import time as `request.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1).lot_stock_id`. If no warehouse exists or `lot_stock_id` is not set, the entire import aborts with a clear configuration error before any row is processed.

**Why:** No location column is needed in the CSV (one decision, applied uniformly), and the existing post-install hook plus initial config already guarantees a warehouse exists in normal operation.

### 3. Per-row state machine

```
  row ──▶ sap_article_code lookup
            │
            ├── not found ─────────▶ ERROR: "SAP code not found"
            │
            ▼
          product.template found
            │
            ├── not rent_ok ──────▶ ERROR: "not a rental product"
            ├── not is_storable ──▶ ERROR: "not storable"
            ├── tracking != serial ▶ ERROR: "not serial-tracked"
            ├── >1 variant ───────▶ ERROR: "ambiguous variant"
            │
            ▼
          product.product resolved (single variant)
            │
            ├── stock.lot for (product, name) exists ─▶ WARN, skip
            │
            ▼
          create stock.lot(product_id, name=serial)
          create stock.quant @ WH/Stock
              with inventory_quantity = 1.0
          stock.quant._apply_inventory()
            │
            ▼
          CREATED ✓
```

Each row is processed in its own savepoint so a single failure does not roll back successful rows.

### 4. Duplicates within the same CSV

If the same `(sap_article_code, serial_number)` pair appears twice in the upload, the first occurrence is processed and the second is treated identically to a pre-existing serial: warned and skipped. This keeps the rule "one serial per product, ever" simple and consistent regardless of whether the duplicate exists in the DB or only in the CSV.

### 5. Accounting via `_apply_inventory()` (not raw stock.move)

We use `stock.quant.with_context(inventory_mode=True).inventory_quantity = 1.0` followed by `_apply_inventory()`. This is the same mechanism the standard *Physical Inventory* UI uses, which means:

- Stock journal entries are created automatically at `product.standard_price`
- Counterpart account is the company's *Inventory Adjustment* account
- Reports and audit trails treat these movements as standard inventory adjustments

**Why not raw `stock.move`:** Lower-level moves require manually picking source/dest locations, costing methods, and posting valuation. `_apply_inventory()` is the documented Odoo way for "I just discovered I have N of these" and gives correct accounting for free.

### 6. Result reporting (JSON, mirrors product import)

```json
{
  "created": 47,
  "skipped": 3,
  "errors": 2,
  "warnings": [
    "Row 4: serial 'SN-2026-001' already exists for FORK-001 — skipped",
    "Row 9: serial 'SN-2026-001' duplicated in CSV for FORK-001 — skipped",
    "Row 17: serial 'SN-X-002' already exists for DRILL-A — skipped"
  ],
  "row_errors": [
    "Row 12: SAP code 'FORK-999' not found",
    "Row 18: product 'DRILL-B' is not serial-tracked"
  ]
}
```

`skipped` and `errors` are separated so the user can tell at a glance whether the file was malformed (errors) or simply re-running an already-loaded import (skipped only).

### 7. Buttons placement

Two new buttons on the rental product tree view header, immediately after the existing "Import Products" button: **Download Serial Template**, **Import Serials**. Visible only in the rental product list (context `in_rental_app`), matching the existing pattern.

## Risks / Trade-offs

- **[Variant ambiguity]** — `sap_article_code` lives on `product.template`. If a template has 2+ variants (e.g., Forklift in Red and Blue), the importer cannot decide which variant the serial belongs to. We error the row. **Mitigation:** Document in the config guide that rental products should use a single variant; if variants are needed, each combination must have its own `sap_article_code`. Acceptable risk because most rental fleets are not configured with variants.

- **[Cost not set before import]** — If `standard_price = 0` at import time, serials are created with zero valuation. Re-running with the correct cost does not re-value existing quants (Odoo cost layers are point-in-time). **Mitigation:** Configuration guide explicitly states "set standard_price on every rental product before importing serials"; consider adding a pre-import validation that warns if any matched product has `standard_price = 0`.

- **[No undo button]** — Once imported and posted, undoing requires a reverse inventory adjustment plus archiving the lots. Acceptable: this is a setup-time tool, not an operational one, and serials are uniquely keyed so re-running is safe (warns and skips).

- **[Large CSV files]** — Entire file is loaded into memory and processed row-by-row. For a fleet of <10K units this is fine. If needed later, can add chunked processing.

- **[Multi-company]** — Uses `request.env.user.company_id` (resolved via the `cids` cookie like the existing controller). Cross-company imports (uploading rows for products in different companies) are not supported in v1.

## Migration Plan

This is a new capability — no migration needed. Sequence for users:

1. Install/upgrade `ggg_rental` (gets the new endpoints and buttons)
2. Set `standard_price` on every rental product (via product import or manually)
3. Accountant prepares to retire the prior fleet asset row (if any) with a one-time JE
4. Download the serial template, fill in serials, upload
5. Verify serials appear at WH/Stock with correct valuation in the Stock Valuation report
6. Accountant posts the offsetting JE to retire the old fleet asset
