## Context

The rental product CSV controller (`rental_csv.py`) defines `PRODUCT_FIELDS` — a static list that drives both the download template headers and the import parser. Three fields added to `product.template` after the controller was written are absent from this list: `deposit_price`, `sale_ok`, and `taxes_id`.

`deposit_price` and `sale_ok` are scalar fields (Float and Boolean) and follow the same patterns already used for `list_price` and `rent_ok`. `taxes_id` is a Many2many to `account.tax` and requires a serialization decision.

## Goals / Non-Goals

**Goals:**
- Add `deposit_price`, `sale_ok`, `taxes_id` to `PRODUCT_FIELDS`, the example row, and `_prepare_product_vals()`
- Round-trip correctly: download → fill → import sets all three fields

**Non-Goals:**
- Changing the pricing template (`download_pricing_template`) — unaffected
- Supporting pricelist-specific taxes or multiple tax groups
- Modifying any model or view

## Decisions

**`taxes_id` CSV representation — semicolon-separated tax names**

Tax names are looked up against `account.tax` filtered by `type_tax_use='sale'` and matched by `name`. Multiple taxes are joined with `;` on download (if ever present) and split on `;` on import.

Alternatives considered:
- Tax `id` — not human-readable, breaks across databases
- Single tax only — too restrictive; semicolon approach handles both cases with no extra complexity

**Column order — insert before pricing columns**

New fields are appended to the product section, before recurrence pricing columns. This keeps the template grouped logically: identity → pricing → rental rates → taxes → import columns.

Final column order:
```
sap_article_code, name, type, categ_id, list_price, sale_ok, rent_ok,
extra_hourly, extra_daily, deposit_price, uom_id, tracking, taxes_id,
default_code, barcode, description_sale, [recurrence columns...]
```

**Empty `taxes_id` on import — leave existing taxes unchanged vs. clear**

Empty cell = skip (do not modify taxes). A cell with a value replaces taxes with the resolved set. This matches the merge semantics used for pricing columns.

## Risks / Trade-offs

- Tax name matching is locale-sensitive — lookup uses the installed language. If tax names differ between databases, import will silently skip unresolved taxes and add a warning. → Mitigation: warning added to import response for unresolved tax names.
- `deposit_price` is company-dependent (`company_dependent=True`) — the import writes using the current user's company, which is correct for single-company setups.
