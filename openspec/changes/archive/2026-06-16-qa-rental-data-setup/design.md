## Context

`is_late` on `sale.order` is a computed field: `next_action_date < now()`. `next_action_date` itself is stored and computed from `rental_start_date` (pickup phase) or `rental_return_date` (return phase). Because both dates are stored fields, writing them directly causes Odoo to recompute `rental_status` and `is_late` immediately — no monkey-patching of time needed.

The existing security model has `group_rental_supervisor` for operations staff. QA testers need a separate group so the tool can be restricted without giving testers supervisor access.

## Goals / Non-Goals

**Goals:**
- Let QA testers set a confirmed rental order to "Late Pickup" or "Late Return" by writing dates to the past
- Record every mutation (field, original value, new value) in a permanent log
- Allow one-click revert of an entire scenario run back to original dates
- Block application on orders that are in an incompatible state (wrong rental_status, already cancelled/returned/invoiced, already late)
- Surface skipped orders with per-order reasons in a summary message

**Non-Goals:**
- Simulating states beyond Late Pickup / Late Return at this stage
- Modifying confirmed invoices or stock moves
- Time-travel at the database level (no mocking of `fields.Datetime.now()`)
- Bulk-creating test orders (out of scope for this tool)

## Decisions

### 1. Permanent model, not a wizard

**Decision:** Use `qa.scenario` (a real `models.Model`) rather than `models.TransientModel`.

**Rationale:** QA needs traceability — who ran what scenario, against which orders, and when. Transient records are garbage-collected and provide no audit trail. A permanent model also makes revert reliable (the log always exists until explicitly deleted).

**Alternative considered:** `models.TransientModel` + a separate log model. Rejected because the scenario record itself is useful to keep (QA lead can review what was run before a release).

---

### 2. Date mutation, not a status override field

**Decision:** Write directly to `rental_start_date` / `rental_return_date` to shift the order into a late state, rather than adding a computed override flag.

**Rationale:** This exercises the same code path that real late orders follow. A flag-based override would be a parallel code path that doesn't test the real behaviour. It also avoids adding permanent fields to `sale.order` for QA purposes.

**Risk:** SOL.write() has guards that block date changes for orders in `returned` or `return` status. We guard against this at the scenario level (only apply to orders in `pickup` or `return` status respectively).

---

### 3. Revert per scenario (all-or-nothing)

**Decision:** Revert restores all orders in a scenario run atomically. No partial revert.

**Rationale:** Partial revert creates confusing intermediate states that are hard to reason about. QA either wants the full test environment restored or not. Matches the "apply all" model.

---

### 4. Safety check order

Checks run in this order; first failure disqualifies the order (reason logged in warning summary):

1. `is_rental_order` must be True
2. `state` must be `sale` (confirmed)
3. `rental_status` must match scenario (`pickup` for Late Pickup, `return` for Late Return)
4. Order must not already be `is_late`
5. No posted invoice lines with `qty_to_invoice > 0` (avoid touching orders mid-invoicing)

---

### 5. Days field = positive integer, applied as `now() - timedelta(days=N)`

QA specifies how many days late. Applied at click time (not stored as a scheduled offset). This means the "late by" amount is approximate if reapplied later — acceptable for QA use.

## Risks / Trade-offs

- **SOL write guards**: `sale.order.line.write()` has guards for `start_date`/`return_date` changes on returned orders. We bypass these by writing to `sale.order.rental_start_date` / `sale.order.rental_return_date` directly (order-level), which does not go through SOL.write(). Confirm this triggers correct recompute of `next_action_date` and `is_late`.

- **Revert after partial pickup**: If QA applied "Late Pickup", then someone actually picked up the order (changing `rental_status` to `return`), reverting would restore the original `start_date` but `rental_status` is now `return`. The revert still writes the date but the scenario state will diverge. Mitigation: warn on revert if `rental_status` has changed since apply.

- **No cascade delete guard**: If a `sale.order` is deleted after a scenario is applied, the log `order_id` foreign key becomes invalid. Odoo will raise an integrity error. Mitigation: add `ondelete='cascade'` on the log's `order_id` field so logs are cleaned up with the order.

## Migration Plan

No migration needed — new models only. The module installs cleanly. Existing data is untouched.

Rollback: uninstall the QA sub-module (if implemented as a separate addon) or remove the new models and views. No data loss to production records since QA tool only writes dates on test orders.

## Open Questions

- Should the QA tool be a sub-module (`ggg_rental_qa`) to allow installing only on non-production databases, or integrated directly into `ggg_rental` behind the group? A sub-module is safer for prod hygiene but adds packaging overhead.
