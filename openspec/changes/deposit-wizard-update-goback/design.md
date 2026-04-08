## Context

The deposit validation wizard (`rental.deposit.sync.wizard`) currently has three buttons: Update & Continue, Continue As-Is, Cancel. This adds a fourth option.

## Goals / Non-Goals

**Goals:**
- Add an "Update & Go Back" button that syncs deposits and closes the wizard

**Non-Goals:**
- Changing any existing button behavior

## Decisions

### 1. Method implementation

Add `action_update_and_goback()` on the wizard. It calls `order_id.action_sync_deposits()` then returns `{'type': 'ir.actions.act_window_close'}` to close the wizard and return to the order form.

### 2. Button placement

Place between "Update & Continue" and "Continue As-Is" in the wizard footer.
