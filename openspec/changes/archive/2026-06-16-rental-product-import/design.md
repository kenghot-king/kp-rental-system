## Context

The ggg_rental module extends Odoo 19 CE with rental functionality. Products have rental pricing rules via `product.pricing` (One2many from `product.template`), each linked to a `sale.temporal.recurrence` (e.g., 1 Hour, 1 Day, 1 Week). Currently the system has 11 recurrence periods. Users manage products with SAP-based inventory codes that need to persist as a reference key.

Current product creation is manual and one-at-a-time through the Odoo UI.

## Goals / Non-Goals

**Goals:**
- Enable bulk import of rental products with pricing from a single CSV file
- Provide dynamic CSV templates that reflect current system configuration
- Use `sap_article_code` as a stable, unique business key for upsert logic
- Support idempotent imports (re-import updates, doesn't duplicate)

**Non-Goals:**
- Replacing Odoo's standard import mechanism for non-rental products
- Variant-level pricing in CSV (template-level only for now)
- Export of existing products to CSV (import only)
- Pricelist-specific pricing in CSV

## Decisions

### 1. Single CSV with dynamic pricing columns (not two-file import)

Pricing periods appear as column headers dynamically generated from `sale.temporal.recurrence` records.

```
sap_article_code, name, ..., 1 Hour, 1 Day, 1 Week, 1 Month
SAP-001, Projector, ..., 200, 1000, 5000, 15000
```

**Why over two-file import:** Single file is simpler for users, eliminates name-matching issues between files, and keeps product + pricing atomic per row.

**Why over Odoo standard import:** Standard import can't handle dynamic pricing columns or merge semantics. It also requires external IDs or name matching for related records.

### 2. `sap_article_code` as match key (not `default_code` or `name`)

- `name` is not unique (duplicates already exist in DB)
- `default_code` is Odoo's internal reference, already has its own meaning
- `sap_article_code` is a dedicated business key controlled by the user

Field spec: `fields.Char(string="SAP Article Code", required=True, index=True, copy=False)`
Uniqueness enforced via SQL constraint.

### 3. Merge semantics for pricing (not full replace)

| CSV cell state | Action |
|---|---|
| Has value (e.g., "1000") | Create or update pricing for that period |
| Empty string | Delete existing pricing for that period |
| Column not in CSV | Keep existing pricing untouched |

**Why:** Users may download a template with fewer columns than the system has recurrences. Full replace would accidentally delete pricing for periods not in the CSV.

### 4. Custom controller (not extending base_import)

Two new endpoints on `ggg.rental` controller:
- `GET /ggg_rental/download_product_template` — dynamic CSV with product fields + recurrence columns + example row
- `GET /ggg_rental/download_pricing_template` — dynamic CSV with just sap_article_code + recurrence columns (for updating pricing only on existing products)
- `POST /ggg_rental/import_products` — processes uploaded CSV, returns JSON result with created/updated/error counts and warnings

**Why not extend base_import:** The dynamic column matching and merge pricing logic don't fit Odoo's standard import pipeline. A custom controller is cleaner and gives better error reporting.

### 5. Buttons placement: rental product tree view header

Two download buttons + one import button visible only in the rental product list view (context `in_rental_app`).

## Risks / Trade-offs

- **[Existing products have no sap_article_code]** → Field is required but existing products don't have values. Migration: make field required at Python level but allow NULL in DB initially. Show warning banner until all products have codes assigned.

- **[Recurrence display_name is translated]** → Column headers use `duration_display` which is translated. Since we decided English-only headers, we force `en_US` context when generating templates and matching columns during import.

- **[Large CSV files]** → No streaming; entire file loaded into memory. Acceptable for product catalogs (unlikely >10K rows). If needed later, can add chunked processing.

- **[Concurrent imports]** → No locking mechanism. Two simultaneous imports of the same product could race. Acceptable risk for admin-only feature.

## Migration Plan

1. Add `sap_article_code` column (nullable at DB level initially)
2. Module upgrade adds the field
3. Admin populates codes for existing products (manually or via script)
4. Once all products have codes, consider adding DB NOT NULL constraint
