## Context

Odoo CE's `account` module ships `report_invoice_document` as the standard invoice QWeb template. `l10n_th` extends it with `primary="True"` to add branch name and changes the title to "Tax Invoice". The wrapper template `account.report_invoice` uses `o._get_name_invoice_report()` to select which template variant to call — the base returns `'account.report_invoice_document'`, l10n_th adds an `t-elif` for `'l10n_th.report_invoice_document'`.

`ggg_rental` already depends on `l10n_th`. `num2words` with `lang='th'` and `to='currency'` is installed and produces correct Thai baht words (verified). The new template must fit into the existing elif dispatch pattern without breaking l10n_th or base Odoo.

## Goals / Non-Goals

**Goals:**
- All `out_invoice` PDFs render using the new Thai-format template
- Template matches the King Power invoice layout: bilingual header, 4-column line table (NO. / DESCRIPTION / VAT CODE / AMOUNT), VAT vs NON-VAT subtotal split, WHT deduction row, Thai baht amount in words, cheque note, dual signature blocks
- Co-exist cleanly with l10n_th (branch name field still available)
- Amount in Thai words auto-computed from `o.amount_total` using `num2words`

**Non-Goals:**
- Per-customer or per-document template switching
- Credit note / refund template changes (out of scope for now)
- Modifying any accounting logic, tax computation, or payment flows
- Supporting non-THB currencies differently (Net Amount row still shows, just in foreign currency)

## Decisions

### 1. Override `_get_name_invoice_report()` unconditionally

**Decision:** Override on `account.move` in `ggg_rental` to always return `'ggg_rental.report_invoice_document'`.

**Rationale:** The wrapper template `account.report_invoice` dispatches on this method. This is the documented extension point. Overriding it is cleaner than xpath-patching the wrapper to remove the `t-if` condition.

**Alternative considered:** Patch the wrapper via xpath to remove the existing `t-if` and replace with an unconditional call. Rejected — more brittle, breaks if Odoo or l10n_th changes the wrapper structure.

### 2. New primary QWeb template (not inherit + replace)

**Decision:** Create `ggg_rental.report_invoice_document` as a `primary="True"` template inheriting `account.report_invoice_document`, with a full `position="replace"` on the root node.

**Rationale:** `primary="True"` registers it in the dispatch system. Using inherit keeps the record linked to the base for upgrade tracking.

**Alternative considered:** Standalone template with no inherit. Simpler, but not registered as a report variant — requires changing the `ir.actions.report` record which is harder to maintain across upgrades.

### 3. WHT detection from negative-amount tax lines

**Decision:** In the template, filter `o.line_ids` for lines where `tax_line_id.amount < 0`. Sum their `amount_currency` (absolute value) = WHT amount. Net Amount = `o.amount_total - wht_amount`.

**Rationale:** WHT taxes are configured with `-5%` amount (verified from tax record). The tax lines on the move have a direct link to their source tax via `tax_line_id`. This is more reliable than checking account codes.

**Alternative considered:** Check account type or account code range. Rejected — more fragile, depends on chart of accounts setup.

### 4. VAT / NON-VAT split from invoice line tax_ids

**Decision:** Split `o.invoice_line_ids` into:
- `vat_lines`: lines where `any(t.amount > 0 for t in line.tax_ids)`
- `non_vat_lines`: lines where no positive-amount tax

Sum `price_subtotal` for each group in the template.

**Rationale:** `price_subtotal` is the line amount excluding tax, which is what the Thai invoice shows as the base for each group. Positive-amount taxes = VAT group; zero or absent = NON-VAT.

### 5. Thai amount in words via Python method on `account.move`

**Decision:** Add `amount_in_thai_words` as a regular (non-stored) method (not `@api.depends` computed field) on `account.move`. Called in QWeb as `o.amount_in_thai_words()`.

**Rationale:** Amount in words is presentation-only; no need to store it. A method is simpler than a computed field. `num2words(amount, lang='th', to='currency')` returns correct output — e.g., `"หนึ่งพันห้าร้อยบาทถ้วน"` for 1500.00.

### 6. Add elif to `account.report_invoice` wrapper

**Decision:** Inherit `account.report_invoice` and add an xpath `position="after"` the l10n_th elif (or the base call) to add our elif for `'ggg_rental.report_invoice_document'`.

**Rationale:** Since we override `_get_name_invoice_report()` to always return our name, only our elif ever fires. The l10n_th elif becomes dead code but does not break anything.

## Risks / Trade-offs

- **Upgrade risk**: If Odoo changes `report_invoice_document` structure significantly, our `primary="True"` template inheriting it may need manual update. → Mitigation: keep inherit_id reference, review on each Odoo version bump.
- **l10n_th conflict**: If l10n_th also overrides `_get_name_invoice_report()` in a future version, our override (loaded after) would win — which is desired. → Low risk currently.
- **Credit notes**: `out_refund` also uses `report_invoice`; our template will render for refunds too. The title "INVOICE ORIGINAL" would be incorrect. → Acceptable for now; add a `t-if` on `o.move_type` to switch title text as a minor follow-up.
- **Non-THB invoices**: `amount_in_thai_words` always calls `num2words(..., lang='th', to='currency')` which outputs "บาท". For USD invoices this is wrong. → Add a guard: only render Thai words if `o.currency_id.name == 'THB'`, else fall back to `o.currency_id.amount_to_text(o.amount_total)`.

## Migration Plan

1. Deploy updated `ggg_rental` module — no database migration needed (no new stored fields)
2. Existing posted invoices will print with the new layout immediately on next print action
3. Rollback: remove the `_get_name_invoice_report` override and the elif from the wrapper — invoices revert to l10n_th template

## Open Questions

- Should credit notes (`out_refund`) use a different title / layout? → Deferred.
- Should the "Page X / Y" counter use Odoo's built-in pager or a custom one? → Use `web.external_layout` built-in pager.
