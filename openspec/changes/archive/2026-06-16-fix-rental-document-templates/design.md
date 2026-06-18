## Context

The rental system generates PDFs via Odoo's QWeb engine using WeasyPrint. Three report templates are affected:

1. `rental_contract_templates.xml` — the main rental contract (สัญญาเช่า)
2. `report_invoice_thai.xml` — the Thai tax invoice / receipt
3. Sale order quotation report — inheriting from `sale.report_saleorder`

WeasyPrint has limited CSS flexbox support compared to browsers. Bootstrap's `h-100` utility depends on flexbox parent height propagation which WeasyPrint does not reliably implement, causing unequal box heights in PDFs. All layout fixes must use HTML `<table>` elements or explicit inline CSS rather than Bootstrap grid classes where equal sizing matters.

## Goals / Non-Goals

**Goals:**
- Equal-height lessor/lessee boxes in rental contract PDF
- Contract "วันที่" shows rental start date in `dd/MM/yyyy` format
- No company-address overlap on contract pages 2+
- Signature section always starts on its own page
- Quotation PDF omits the T&C URL block
- Thai invoice customer-info and payment-info sections have no cell borders

**Non-Goals:**
- Redesigning the overall layout or branding of any report
- Changing data shown (fields, calculations, Thai word amounts)
- Fixing any issues on the Odoo UI side (screen views)
- Modifying the real rental contract T&C text (awaiting content from client)

## Decisions

### D1 — Party boxes: table layout instead of Bootstrap grid

**Decision:** Replace `<div class="row"><div class="col-6">` with a two-cell `<table>` for the lessor/lessee block.

**Rationale:** WeasyPrint treats each Bootstrap col as a block-level box; `h-100` requires the parent flex container to have an explicit height, which `row` does not provide in WeasyPrint's CSS model. HTML `<table>` auto-equalises row cell heights unconditionally across all renderers.

**Alternative considered:** Add `display:flex; align-items:stretch` inline on the row div. Rejected — WeasyPrint flexbox support is incomplete and would require testing every WeasyPrint version upgrade.

### D2 — Contract date: use `rental_start_date` with `date` widget

**Decision:** Change line 39 of `rental_contract_templates.xml` from `doc.date_order` to `doc.rental_start_date` with `t-options='{"widget":"date"}'`.

**Rationale:** The document date on a rental contract logically represents when the rental begins, not when the order was created. The `date` widget formats datetime fields as date-only using the partner's locale (Thai locale = `dd/MM/yyyy`).

**Note:** `rental_start_date` is a `Datetime` field; the `date` widget strips the time component automatically.

### D3 — Company address overlap: page-body top margin via CSS

**Decision:** Add a `<style>` block inside the template's `<t t-call="web.external_layout">` wrapper that sets `@page { margin-top: 60mm; }` (or equivalent) to push body content below the running header.

**Rationale:** `web.external_layout` injects a `position: running(header)` block containing company info. This block occupies the top page margin. If `@page margin-top` is too small, the header overflows into body content on pages 2+. The fix is a template-level style override, not a global change.

**Alternative considered:** Switch to `web.basic_layout` and manually render the company header only on page 1. Rejected — too invasive; `web.external_layout` handles logo, company info, and footer consistently across all Odoo reports.

### D4 — Signature section: explicit page break

**Decision:** Add `style="page-break-before: always;"` to the signature `<div class="mt-5">` wrapper (line 215 in the contract template).

**Rationale:** The terms-and-conditions block (`doc.company_id.rental_contract_terms`) is variable-length HTML; its length cannot be predicted. A forced page break is the only reliable way to guarantee the signature section starts on a fresh page regardless of T&C length.

### D5 — Quotation T&C: XPath suppress

**Decision:** Add a QWeb template inheritance in `ggg_rental` that overrides the T&C / note block in `sale.report_saleorder` with `t-if="False"`.

**Rationale:** The T&C link (`/terms`) is rendered by the standard `sale` module inside `report_saleorder_document`. An XPath targeting the `<p t-if="doc.note">` or the terms anchor is the minimal, upgrade-safe approach.

**Alternative considered:** Clear `note` field via Python override. Rejected — would destroy data; the note field may contain other content.

### D6 — Thai invoice: remove borders via inline style

**Decision:** In `report_invoice_thai.xml`, remove `border` and `border-collapse` from the outer customer-info table, and add `border: none` to all `<td>` elements in that section and the payment-info block.

**Rationale:** The borders come from the table's default rendering combined with `border-collapse:collapse`. Explicitly setting `border: none` on `<td>` and removing any `border` shorthand on `<table>` eliminates them without touching unrelated sections.

## Risks / Trade-offs

- **D3 margin value is a guess** → Test with actual WeasyPrint output; adjust `margin-top` value until header clears correctly. Start with `55mm`.
- **D5 XPath target may shift with Odoo upgrades** → The XPath is against a stable part of `sale.report_saleorder_document`; low risk for minor Odoo updates.
- **D4 page break always fires** → If T&C is very short, this creates a near-blank page before signatures. Acceptable trade-off given variable T&C length.

## Migration Plan

All changes are pure QWeb template XML edits — no Python migrations, no database changes. Deploy by restarting the Odoo service after module upgrade:

```bash
odoo -u ggg_rental
```

Rollback: revert the XML files and upgrade again.

## Open Questions

- Exact WeasyPrint `margin-top` value for the company header — to be validated by printing a test contract.
- Actual XPath selector for the T&C block in `sale.report_saleorder_document` — confirm field name (`note` vs `terms_and_conditions`) in Odoo 19.
