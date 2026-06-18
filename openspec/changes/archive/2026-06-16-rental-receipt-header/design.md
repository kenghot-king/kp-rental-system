## Context

The `thai-invoice-template` change (complete, 20/20 tasks, not yet archived) added a QWeb template `ggg_rental.ggg_report_invoice_document` that renders every `out_invoice` with a fixed bilingual title "ต้นฉบับ ใบแจ้งหนี้ / INVOICE ORIGINAL". The override is wired through `account.move._get_name_invoice_report()` in `addons/ggg_rental/models/account_move.py`.

In Thai accounting practice the business never hands a customer an "invoice original" — by the time a document is printed it represents a paid transaction and therefore a receipt. If the transaction contains VAT-bearing items the single document is legally a combined "ใบเสร็จรับเงิน/ใบกำกับภาษี" (Receipt / Tax Invoice); otherwise it is a plain "ใบเสร็จรับเงิน". Credit notes print as "ใบลดหนี้".

The VAT-vs-NON-VAT split already exists in the template:

```xml
<t t-set="vat_lines"
   t-value="product_lines.filtered(lambda l: any(t.amount &gt; 0 for t in l.tax_ids))"/>
```

— so the signal needed to drive the conditional header is already computed; only the title block needs to consume it.

## Goals / Non-Goals

**Goals:**
- The only printable customer-facing `out_invoice` is a paid one, and the printed header matches Thai receipt conventions.
- The guard covers every PDF render path (toolbar print button, cog-menu action, direct `/report/pdf/...` URL, email preview).
- `out_refund` remains printable at any time with header "ใบลดหนี้".
- No change to any layout element below the title (customer block, line items, VAT split, WHT, signatures, Thai words).

**Non-Goals:**
- No new English subtitle on the receipt header. Kept Thai-only for now; adding a bilingual line is a future change.
- No separate `ir.actions.report` for receipts vs. invoices — it's one template whose title branches.
- No change to the `thai-invoice-template` change itself; this change supersedes its title requirement via the spec delta.
- No change to deposit-invoice workflow, pickup-payment-gate, or any existing print-related logic other than the gate described here.
- No behavior change for `out_invoice` of non-THB currency beyond what the title logic requires.

## Decisions

### Decision 1: Raise `UserError` from `_get_name_invoice_report()` to gate printing

We extend the existing override in `account.move._get_name_invoice_report()`:

```python
def _get_name_invoice_report(self):
    self.ensure_one()
    if self.move_type == 'out_invoice' and self.payment_state != 'paid':
        raise UserError(_("ไม่สามารถพิมพ์ใบเสร็จได้ เนื่องจากยังไม่ชำระเงิน"))
    return 'ggg_rental.ggg_report_invoice_document'
```

**Why here:** `_get_name_invoice_report()` is called by `account.move._get_invoice_report()` which in turn is invoked from every PDF render path — the form-view print button, the cog-menu report binding, direct URL `/report/pdf/...`, and the email-send flow. A single override therefore blocks all paths without view-level patching.

**Alternatives considered:**
- *View-level `invisible` on the Print button.* Rejected: only hides the cog button, leaves URL and email paths unguarded.
- *Override `ir.actions.report._render_qweb_pdf` for the specific report.* Rejected: more intrusive, harder to test, and duplicates a check that has a natural home on the model.
- *Compute a `can_print` field and gate on it in views.* Rejected: still a view-level change, and leaks terminology ("can_print") into the UI when the intent is a hard server-side rule.

### Decision 2: Conditional title driven by `move_type` + `vat_lines`

In the template's title block:

```xml
<t t-set="has_vat" t-value="bool(vat_lines)"/>

<div style="text-align:center; margin:6px 0 10px 0;">
    <strong style="font-size:13pt;">
        <t t-if="o.move_type == 'out_refund'">ใบลดหนี้</t>
        <t t-elif="has_vat">ใบเสร็จรับเงิน/ใบกำกับภาษี</t>
        <t t-else="">ใบเสร็จรับเงิน</t>
    </strong>
</div>
```

**Why:** `vat_lines` is already set earlier in the template for the VAT/NON-VAT subtotal rows. Reusing it keeps the VAT-detection rule in exactly one place and avoids drift. The rule — "any product line has a tax with `amount > 0`" — intentionally treats VAT 0% as no-VAT per stakeholder decision; zero-rated exports fall back to the plain receipt header.

**Alternatives considered:**
- *Derive from `o.amount_tax > 0`.* Rejected: `amount_tax` sums positive tax amounts across the move and would be zero when the only taxes are WHT (negative) — but it would also be zero in a 0% VAT case, giving the same visible result. The reason we prefer `vat_lines` is that it's already computed and scoped to product lines, keeping one source of truth.
- *Classify by tax group.* Rejected: requires partners to have correctly-configured tax groups; amount-based detection is more robust to data variation.

### Decision 3: No English subtitle

The existing `INVOICE ORIGINAL` English subtitle is removed entirely. No English substitute is added. Stakeholder confirmed Thai-only for now.

### Decision 4: Archive ordering

This change's delta targets the `thai-invoice-pdf` capability with MODIFIED/ADDED requirements. That capability is not yet in `openspec/specs/` because the `thai-invoice-template` change — which introduces it — is complete but unarchived. **`thai-invoice-template` must be archived before `rental-receipt-header` is archived.** At implementation time this is not blocking: the code edits target the same files regardless.

## Risks / Trade-offs

- **Risk:** `_get_name_invoice_report()` is called in non-print contexts (e.g. some flows that resolve the template name for preview / caching). Raising `UserError` there could surface user-visible errors in unexpected places. → **Mitigation:** the stock call sites in Odoo 19 are the PDF render and the report-binding resolution; both are print-intent paths. If a future flow needs the template name without intending to print, we add a skip via `self.env.context.get('bypass_receipt_gate')` and document it.
- **Risk:** Users currently rely on printing unpaid invoices for internal review. → **Mitigation:** confirmed with stakeholder; not a supported workflow. Workaround if needed: view the invoice in the web UI, or export via a custom internal report later.
- **Risk:** Invoices in `in_payment` (payment recorded but not reconciled) would be blocked despite being effectively paid. → **Mitigation:** stakeholder decision is strict `paid` only; they can manually reconcile to unlock printing. If this becomes operationally painful we revisit and broaden the gate.
- **Trade-off:** Removing the English subtitle makes the document slightly less legible to non-Thai readers. Accepted for Thai-only rollout; re-add as a later change if cross-border customers need it.
- **Risk:** The `vat_lines` filter excludes `display_type != 'product'`, so a section or note with tax metadata would not influence the title. Acceptable — only product lines drive receipt semantics.
