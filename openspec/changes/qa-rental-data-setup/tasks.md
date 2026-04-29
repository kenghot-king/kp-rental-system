## 1. Security & Access

- [x] 1.1 Add `group_qa_tester` to `security/security.xml`
- [x] 1.2 Create `security/ir.model.access.csv` entries for `qa.scenario` and `qa.scenario.log` (QA tester: read/write scenario, read-only log)

## 2. Models

- [x] 2.1 Create `models/qa_scenario.py` with `qa.scenario` model: fields `name`, `scenario` (selection: late_pickup/late_return), `days` (integer, default=1), `order_ids` (m2m sale.order), `state` (draft/applied/reverted), `log_ids` (o2m)
- [x] 2.2 Create `models/qa_scenario_log.py` with `qa.scenario.log` model: fields `scenario_id`, `order_id` (ondelete=cascade), `field_changed`, `original_value` (Datetime), `new_value` (Datetime), `applied_by` (res.users), `applied_at` (Datetime), `reverted` (Boolean)
- [x] 2.3 Implement `action_apply()` on `qa.scenario`: safety checks, date mutation, log creation, state → applied
- [x] 2.4 Implement `action_revert()` on `qa.scenario`: restore dates from log, mark log entries reverted, warn if rental_status changed, state → reverted
- [x] 2.5 Add `models/__init__.py` imports for both new models
- [x] 2.6 Register models in `models/__init__.py` of `ggg_rental`

## 3. Views

- [x] 3.1 Create `views/qa_scenario_views.xml`: form view (name, scenario, days, order_ids, state, Apply/Revert buttons, log_ids tab), list view
- [x] 3.2 Create `views/qa_scenario_log_views.xml`: read-only list view with columns: order, scenario, field_changed, original_value, new_value, applied_by, applied_at, reverted
- [x] 3.3 Create ir.actions.act_window for both models

## 4. Menu

- [x] 4.1 Add QA section to `views/sale_renting_menus.xml` inside `rental_menu_root`: parent menu item, Scenarios submenu, Logs submenu — all gated on `group_qa_tester`

## 5. Module Registration

- [x] 5.1 Add new XML files to `__manifest__.py` data list (security.xml, ir.model.access.csv, qa_scenario_views.xml, qa_scenario_log_views.xml, sale_renting_menus.xml already listed — just new files)
- [x] 5.2 Restart Odoo and upgrade `ggg_rental` to verify models install cleanly

## 6. Verification

- [x] 6.1 Assign `group_qa_tester` to a test user; confirm QA menu is visible only to that user
- [x] 6.2 Create a confirmed rental order (rental_status=pickup), apply a Late Pickup scenario (days=2), verify `is_late=True` and log entry created
- [x] 6.3 Apply a Late Return scenario to an order with rental_status=return, verify `is_late=True`
- [x] 6.4 Test all safety check paths: wrong status, already late, non-rental order — verify skipped with correct reason in warning
- [x] 6.5 Revert the scenario, verify original dates restored and `is_late=False`
- [x] 6.6 Verify re-applying an applied scenario raises UserError
