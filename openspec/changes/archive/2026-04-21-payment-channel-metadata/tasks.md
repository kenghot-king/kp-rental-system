## 1. Journal Model Extension

- [x] 1.1 Add `channel_type` Selection field to `account.journal` with values `cash`, `edc`, `qr`, `online`, `other` (default empty, not required)
- [x] 1.2 Register `account.journal` model extension in `ggg_rental/models/__init__.py`

## 2. Journal Form View

- [x] 2.1 Inherit `account.journal` form view to show `channel_type` in the journal configuration area (near Type)
- [x] 2.2 Add `channel_type` to the journal list view filters / group-by options

## 3. Payment Model Extension

- [x] 3.1 Add `cashier_id` Many2one(`res.users`) field to `account.payment` (default `lambda self: self.env.user`, tracked)
- [x] 3.2 Add `approval_code` Char field to `account.payment` (not required, not conditional)
- [x] 3.3 Add `display_method` Char field to `account.payment` as stored computed, depending on `payment_method_line_id` and `payment_method_line_id.name`, returning `self.payment_method_line_id.name or False`
- [x] 3.4 Confirm field registration is included in existing `ggg_rental/models/account_payment.py` (extending the model from `rental-payment-refs`)

## 4. Payment Form View

- [x] 4.1 Inherit `account.payment` form view to show `cashier_id` (readonly-ish, but visible), `approval_code`, and keep existing `payment_reference` / `payment_reference_2` placement unchanged
- [x] 4.2 Ensure `cashier_id` is visible on all payments (not rental-gated) — it is a universal attribution field

## 5. Payment Register Wizard

- [x] 5.1 Add `approval_code` Char field to `account.payment.register`
- [x] 5.2 Override `_create_payment_vals_from_wizard` (or the Odoo 19 equivalent) to populate `cashier_id = self.env.user.id` and pass `approval_code` through to the created `account.payment`
- [x] 5.3 Inherit the register wizard form view to show `approval_code` (always visible — no conditional `invisible` attr)
- [x] 5.4 Do NOT expose `cashier_id` in the wizard view (auto-populated server-side only)

## 6. Admin Configuration Guidance (docs, not code)

- [x] 6.1 Document in the change folder the expected post-install admin steps: set `channel_type` on each rental-facing journal, and configure `inbound_payment_method_line_ids` per journal with display names (VISA, Mastercard, JCB, AMEX, UnionPay, PromptPay QR, Credit Card, Internet Banking, TrueMoney, Cash, etc.)

## 7. Module Registration

- [x] 7.1 Add new view XML files to `ggg_rental/__manifest__.py` `data` list
- [x] 7.2 Verify module upgrade installs the new fields without breaking existing `rental-payment-refs` behavior

## 8. Verification

- [x] 8.1 Manual test — register a payment as user A; confirm `cashier_id` is set to A
- [x] 8.2 Manual test — configure 3 method lines on an EDC journal; confirm Pay wizard dropdown shows only those 3
- [x] 8.3 Manual test — enter an approval code on the wizard; confirm it appears on the created payment
- [x] 8.4 Manual test — rename a method line from "VISA" to "VISA Card"; trigger a recompute and confirm `display_method` updates on existing payments
- [x] 8.5 Manual test — leave `channel_type` empty on a journal; confirm payments still register normally
