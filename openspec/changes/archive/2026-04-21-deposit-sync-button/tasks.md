## 1. Sync Deposits Button

- [x] 1.1 Add `action_sync_deposits()` method on `sale.order` — creates missing, updates drifted, removes orphaned deposit lines
- [x] 1.2 Add [Sync Deposits] button in the rental order form view above order lines, visible only on rental orders in draft/sent state

## 2. Deposit Validation Check

- [x] 2.1 Add `_check_deposit_sync()` read-only method on `sale.order` — returns list of mismatch descriptions or False if in sync

## 3. Validation Wizard

- [x] 3.1 Create `rental.deposit.sync.wizard` transient model with fields: `order_id`, `original_action`, `mismatch_info`
- [x] 3.2 Add wizard methods: `action_update_and_continue()`, `action_continue_as_is()`
- [x] 3.3 Create wizard form view with mismatch info display and three buttons (Update & Continue, Continue As-Is, Cancel)
- [x] 3.4 Register wizard model in `__init__.py` and add view to `__manifest__.py`

## 4. Action Interception

- [x] 4.1 Override `action_quotation_send()` (Send) — check deposits, return wizard if mismatch
- [x] 4.2 Override Confirm action — check deposits, return wizard if mismatch
- [x] 4.3 Override Print action — check deposits, return wizard if mismatch
- [x] 4.4 Override Preview action — check deposits, return wizard if mismatch

## 5. Cleanup

- [x] 5.1 Remove leftover auto-sync code from `auto-deposit-line` if any remains (verify `sale_order.py` and `sale_order_line.py` write override are clean)
