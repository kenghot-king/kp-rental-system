## Context

The `sale_document_tax_totals_no_currency` template in `rental_order_report_templates.xml` inherits from `sale.document_tax_totals` and overrides the total row to format amounts without a currency symbol. The base template's `o_total` row contains two `<strong>` elements: one for the label "Total" and one for the amount value. The current XPath `//tr[@class='o_total']//strong` matches both, replacing both with the formatted number.

The rental contract template's deposit section (`เงินประกัน`) is a `<div>` block that flows directly after the rental items table with no page separation enforced.

## Goals / Non-Goals

**Goals:**
- Restore the "Total" label text in the quotation/sale order PDF total row
- Force the deposit section to always begin on a new page in rental contract PDFs

**Non-Goals:**
- Changing the formatting logic (number format, currency suppression) of the total row
- Modifying the deposit section's content or table structure
- Affecting any other report templates

## Decisions

**XPath specificity fix**: Use `//tr[@class='o_total']/td[last()]//strong` instead of `//tr[@class='o_total']//strong`. This targets only the last `<td>` (the amount cell), leaving the first `<td>` containing `<strong>Total</strong>` untouched.

Alternative considered: targeting by `td[@class='text-end']` — rejected because if Odoo ever adds another text-end cell before the amount it would break. `td[last()]` is more robust since the amount is always the last column.

**Page break**: Add `style="page-break-before: always;"` on the existing deposit section `<div>` wrapper at line 142. This is the standard CSS/WeasyPrint approach used elsewhere in the codebase (`page-break-inside: avoid` already appears at line 177).

## Risks / Trade-offs

- [XPath change] If Odoo upgrades the base `o_total` row structure to add more `<td>` elements, `td[last()]` would still select the last cell correctly → Low risk
- [Page break] Forces a new page even for short contracts where deposit fits naturally — acceptable per user requirement
