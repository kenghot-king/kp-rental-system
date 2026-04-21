## Context

Deposit lines on rental orders are created/updated by `action_sync_deposits()` on `sale.order`. Currently:
- Price is sourced from `line.product_id.list_price` — the rental product's general sale price, not a deposit-specific amount
- Tax is sourced from `line.tax_ids` — the rental line's taxes (fiscal-position mapped), not the deposit product's own taxes
- `_check_deposit_sync()` flags a mismatch if the deposit price drifts from `list_price`

The deposit product (`rental_deposit_product_id`) is configured per-company in Rental Settings and carries its own `taxes_id`. Tax should originate from this product, not the rental line.

## Goals / Non-Goals

**Goals:**
- Provide a dedicated, company-dependent `deposit_price` field on `product.template` for rental products
- Use `deposit_price` as the canonical price source for deposit lines
- Use the deposit product's `taxes_id` as the canonical tax source for deposit lines
- Expose `deposit_price` in the rental tab of the product form
- Remove price drift detection from `_check_deposit_sync()` (price on deposit lines is set once at sync time and not re-validated)

**Non-Goals:**
- No fiscal position mapping on deposit line taxes — taxes come directly from `deposit_product.taxes_id`
- No UI changes to the rental order deposit lines (already readonly)
- No migration of existing deposit lines

## Decisions

### `deposit_price` on `product.template`, not `product.product`
Rental products are typically managed at the template level (no variants). Consistent with how `list_price` and `extra_hourly`/`extra_daily` are accessed via template. Using `company_dependent=True` so each company can set its own deposit expectation per product.

### Tax source: `deposit_product.taxes_id`, not rental line's `tax_ids`
The deposit product is a service product with its own tax configuration (e.g., exempt, or a specific VAT rate). Using the deposit product's taxes ensures the deposit line is always taxed according to the deposit product's rules, regardless of what the rental item is taxed at. Fiscal position is intentionally not applied — the deposit product's taxes are used as-is.

### Remove price check from `_check_deposit_sync()`
The deposit price is now independent of the rental product's `list_price`. Comparing them would produce false positives. The sync check should only validate structural correctness (missing lines, orphaned lines, qty mismatch).

## Risks / Trade-offs

- **`deposit_price = 0` means zero deposit** — no fallback to `list_price`. This is intentional but staff must remember to set it. → Mitigation: field is visible on the rental tab; a future enhancement could add a warning if deposit_price is 0 on a rental product.
- **Existing deposit lines are not updated** — after this change, old deposit lines retain their old price/tax until the user clicks [Sync Deposits]. → No migration needed; the sync button is the mechanism for correction.
- **Tax not fiscal-position mapped** — intentional design choice. If this causes issues for specific customers, it can be revisited in a follow-up change.
