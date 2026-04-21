## Why

When the deposit validation wizard shows mismatches, the user can only "Update & Continue" (sync + proceed with original action) or "Continue As-Is". There's no option to sync the deposits and then go back to review the order before proceeding. Users may want to verify the synced deposit lines look correct before sending/confirming.

## What Changes

- Add an **[Update & Go Back]** button to the `rental.deposit.sync.wizard` form. This button syncs deposits then closes the wizard, returning the user to the rental order form so they can review the updated deposit lines before taking action.

## Capabilities

### New Capabilities
- `deposit-wizard-update-goback`: An "Update & Go Back" button on the deposit sync wizard that syncs deposits and returns to the order.

### Modified Capabilities

## Impact

- **Models**: `rental.deposit.sync.wizard` (new method)
- **Views**: `rental_deposit_sync_views.xml` (new button)
