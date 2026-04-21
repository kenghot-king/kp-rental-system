## Context

The rental business takes payments through many channels: cash, multiple EDC terminals (each accepting VISA/Master/JCB/AMEX/UnionPay), Thai QR to different destination banks, and online gateways. In Odoo today, all of these appear as indistinguishable `account.payment` rows with a generic "Manual Payment" method, making daily cashier reconciliation and channel-based revenue reporting impossible.

A prior change (`rental-payment-refs`) added `payment_reference` (Ref 1) and `payment_reference_2` (Ref 2) on `account.payment` gated by an `is_rental_payment` computed flag. That pattern — extending `account.payment` with rental-scoped metadata plus mirroring fields on `account.payment.register` — is the template this change follows.

This change is the **first of two**. It delivers only categorization and attribution data. A follow-on change `daily-payment-reconciliation` will add the reconciliation model, supervisor confirm flow, and XLSX report that consume this data.

## Goals / Non-Goals

**Goals:**
- Cashier attribution on every payment (who took it)
- Channel classification on every journal (cash/EDC/QR/online/other)
- Per-brand/per-gateway granularity without custom selection fields — use native `account.payment.method.line` infrastructure
- Approval code capture for EDC/QR/online audit trails
- Foundation flag `is_rental_supervisor` on `res.users` so the follow-on reconciliation change can gate confirm actions
- Immediate usability of Odoo's native "Payments Analysis" grouped by `payment_method_line_id`

**Non-Goals:**
- `rental.daily.reconciliation` model or reconciliation UI (follow-on change)
- XLSX daily reconciliation report (follow-on change)
- Variance/shortage-overage journal entries (deferred beyond follow-on)
- `res.branch` / multi-branch scoping
- Automated online payment gateway callbacks
- Data migration of historical payments (new fields simply default empty on existing records)

## Decisions

### 1. Use native `account.payment.method.line` for brand/gateway variants

Instead of adding a custom `card_brand` selection (VISA / Master / JCB / AMEX / UnionPay), configure `inbound_payment_method_line_ids` per journal. Each method line wraps the existing "Manual Payment" method but carries a custom display `name`.

Example admin setup:
- EDC-KBank-Silom-T1 → method lines: [VISA, Mastercard, JCB, AMEX, UnionPay]
- EDC-SCB-Silom-T1 → method lines: [VISA, Mastercard, JCB]
- QR-KBank → method lines: [PromptPay QR]
- Online-Omise → method lines: [Credit Card, Internet Banking, TrueMoney]
- Cash → method lines: [Cash]

**Why not a custom `card_brand` selection?** Native method lines are journal-scoped out of the box (Odoo's Pay wizard already filters the dropdown by journal), are admin-managed data (no code change to add a brand), and generalize across *all* channels uniformly — not just cards. Adding a brand later means creating one database row, not shipping code.

**Why code = 'manual' underneath?** Odoo fires provider-specific behavior hooks on certain codes (e.g. `stripe`, `paypal`, `adyen`). Reusing `code='manual'` guarantees no unexpected side effects while letting the method-line `name` carry the human label.

### 2. `channel_type` on journal is classification-only, not UI logic

`channel_type` is a simple selection on `account.journal`. It does **not** drive field visibility on the Pay wizard or payment form. Its only uses are reporting filters and — in the follow-on change — subtotaling by channel on the reconciliation report.

**Why not use it to hide/show `approval_code`?** An earlier iteration proposed that. Dropped because `approval_code` is useful on every non-cash channel (EDC approval, QR transaction ID, online gateway ref). Always-visible keeps the UI predictable and the rule book short: cashier fills what's applicable, leaves the rest blank.

**Why not reuse standard `journal.type`?** Standard `type` values (`cash`, `bank`, `sale`, `purchase`, `general`, `credit`) are too coarse — every card/QR/online journal is just `type='bank'`. We need a finer split for the rental domain without overloading accounting semantics.

### 3. `cashier_id` = `env.user`, not user-editable on the wizard

Populated server-side in the register wizard's create override. Not exposed as a wizard field.

**Why not editable (supervisor registers on behalf of cashier)?** Out of scope for Phase 1. Adding override capability means also adding permission logic and an audit trail of "who actually entered this on behalf of whom" — a layer of complexity the business hasn't asked for. Can be added later without breaking the contract (flip wizard field visibility on; keep default).

### 4. `display_method` is a stored computed field

Reads `payment_method_line_id.name`. Used as the grouping key for all downstream reports and for the follow-on reconciliation lines.

**Why stored?** Grouping queries in report SQL / ORM read_group need indexable values. Recomputed when `payment_method_line_id` changes or the line's `name` changes.

**Why not just use `payment_method_line_id` directly?** Method lines are journal-scoped — the same brand label ("VISA") exists as multiple separate records across journals. For `(method, journal)` flat reports we *want* the label as a string, not the record ID.

### 5. `is_rental_supervisor` added now, used later

A foundation Boolean. No behavior attached in this change. Added here so the follow-on reconciliation change can reference it for access control without needing a schema migration at that point.

**Why not a group/security role?** Ultimately may evolve into an `ir.model.access.csv`-backed group. For Phase 1 a simple Boolean is sufficient and easy to flip per user. If access needs grow, this field becomes the `implied_ids` membership criterion for a future group.

### 6. `approval_code` is free Char, not structured

No format validation. Different channels write different things (6-digit EDC approval, 20-char QR ref, 30-char gateway UUID).

**Why not split per-channel?** Three structured fields (edc_approval, qr_ref, gateway_ref) triples the form clutter for negligible gain. One free field + the channel context (journal + method line) carries all the information needed.

## Risks / Trade-offs

- **[Risk] Admins forget to configure method lines per journal** — then the Pay wizard shows only the default "Manual Payment" entry and brand distinction is lost. → Mitigation: document the required setup in the change; the follow-on reconciliation change can surface a warning when a journal with `channel_type in ('edc','qr','online')` has ≤1 method line configured.
- **[Risk] Historical payments have no `cashier_id`** — pre-existing rows won't retroactively attribute to a user. → Accepted: reports filter out rows with empty `cashier_id` from cashier-scoped views. No migration needed because historical reconciliation is not in scope.
- **[Risk] `display_method` stale if method line renamed** — stored computed fields don't auto-recompute in every ORM path. → Mitigation: include `payment_method_line_id.name` in the `@api.depends` chain; manual recompute available via scheduled action if drift occurs.
- **[Risk] `channel_type` left empty on a rental journal** — journal excluded from channel reports. → Accepted: spec explicitly allows this and degrades gracefully; the follow-on change can raise a warning rather than a hard constraint.
- **[Risk] Cashier cannot override when registering on behalf of another cashier** — operational friction if one cashier is unavailable. → Accepted for Phase 1 per business decision. Revisit if the rental operations team reports real pain.
- **[Trade-off] No custom `card_brand` field means brand is reporting-only via `display_method`** — you can't write a domain like `[('card_brand','=','visa')]` directly. You filter via `[('display_method','=','VISA')]` or `[('payment_method_line_id','=', ...)]` instead. This is fine for the reports we need; if a future need emerges to treat brand as a first-class dimension, a thin `card_brand` can be added later derived from `display_method`.
