## Context

The `ggg_rental` addon extends Odoo's rental module. Rental orders use `sale.order` with `is_rental_order=True`. Order lines are typed by two flags: `is_rental` (rental product lines) and `deposit_parent_id` (auto-generated deposit lines). Late fine and damage charge lines have neither flag set.

The `group_rental_supervisor` security group already exists in `security.xml` and is used for daily reconciliation access. It needs to be extended to cover paid-order editing.

Invoices (`account.move`) are linked via `order.invoice_ids`. Payment state is tracked on the invoice via `payment_state` (`paid`, `in_payment`, `partial`, `not_paid`).

## Goals / Non-Goals

**Goals:**
- Block editing of rental item lines and deposit lines once any invoice is paid, for non-supervisors
- Block cancellation for all users when any invoice is paid (refund-first policy)
- Allow Rental Supervisors to edit all line types on paid orders
- Leave late fine and damage charge lines editable at all times for everyone
- Enforce cancel restriction at the Python layer (not just UI)

**Non-Goals:**
- Restricting field edits at Python `write()` level (view-level is sufficient for staff workflows)
- Blocking edits to order header fields (customer, dates, etc.)
- Changing permissions on non-rental `sale.order` records
- Modifying the Rental Supervisor group's other existing capabilities

## Decisions

### 1. Two computed fields instead of one

Use separate `has_paid_invoice` and `can_edit_paid_order` fields rather than a single `is_locked` field.

**Why:** `has_paid_invoice` is a pure data fact (usable for cancel button visibility for all users). `can_edit_paid_order` encodes the session-user check. Keeping them separate allows the view to compose them differently for different purposes (cancel button vs. line readonly).

**Alternative considered:** A single `line_edit_locked` field combining both. Rejected because the cancel button needs `has_paid_invoice` alone (applies to supervisors too).

### 2. `can_edit_paid_order` as non-stored computed field

The field returns `self.env.user.has_group(...)` — it does not depend on record data, only on the session user. It is never stored.

**Why:** Stored computed fields based on `env.user` are anti-patterns in Odoo (they'd store a per-user value on a shared record). Non-stored is correct here — it re-evaluates on every read, which is the right semantics for access control.

### 3. Python-level cancel guard only (not write guard)

Override `_action_cancel` to raise `UserError` when `is_rental_order and has_paid_invoice`. Do not add a `write()` override to block line edits.

**Why:** A `write()` guard would also intercept `qty_delivered` updates during pickup/return flows, requiring complex exemption logic. The line edit restriction is a UX/operational safeguard, not a financial integrity constraint — view-level readonly is sufficient for staff use. Cancel, however, is a state transition with accounting consequences, so Python enforcement is warranted.

### 4. View-level readonly via inline domain expressions

Update the existing `<attribute name="readonly">` on the 8 order-line field xpaths to combine the existing `deposit_parent_id` guard with the new payment-lock condition.

Final condition applied to each field:
```
(deposit_parent_id and parent.has_paid_invoice and not parent.can_edit_paid_order)
or (is_rental and parent.has_paid_invoice and not parent.can_edit_paid_order)
```

Simplified: `(deposit_parent_id or is_rental) and parent.has_paid_invoice and not parent.can_edit_paid_order`

**Why not a separate inheriting view with `groups=`?** A groups-based view override would hide the restriction entirely from supervisors rather than exposing the correct editable state. Inline expressions are more transparent and easier to audit.

### 5. Cancel button hidden when paid (all users)

Add `invisible` condition to the standard `action_cancel` button: `is_rental_order and has_paid_invoice`. Python guard is still present as a backstop.

**Why:** Hiding the button prevents confusion — there is nothing a user can do from that button when paid. The error message from the Python guard serves as a secondary safety net if the button is somehow triggered (e.g., via keyboard shortcut or API).

## Risks / Trade-offs

- **Stale `has_paid_invoice` in UI** → The field is non-stored and recomputed on record read. After a payment is registered, the user must reload the form to see the lock applied. This is standard Odoo behavior and acceptable for staff workflows.
- **Supervisor can edit deposit amounts after payment** → This is intentional per requirements, but could allow manual inconsistencies between the deposit invoice and the order line. Operational risk; accepted by design.
- **`payment_state = 'in_payment'` triggers lock** → Payments in transit (bank not yet reconciled) will lock the order. This is conservative but correct — once a payment is registered, the order should be considered committed.

## Migration Plan

No data migration required. The computed fields are non-stored. The view changes take effect on module upgrade (`-u ggg_rental`). Existing paid orders will immediately show the lock on next form open after upgrade.

Rollback: revert the module to previous version and upgrade.

## Open Questions

- Should the lock also apply to the rental date fields (`rental_start_date`, `rental_return_date`) for non-supervisors on paid orders? Currently out of scope per requirements ("everything" is editable by supervisors; date fields are not in the locked set for regular users either). Confirm if date fields should also be locked.
