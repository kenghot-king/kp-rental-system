## Why

There is no formal rental contract document. The existing "Pickup and Return Receipt" is a post-event document that records what was handed over — it is not a pre-event legal agreement. Staff have no way to print a contract for the customer to sign at pickup time, and there is no place to configure company-level rental terms that appear on such a document.

## What Changes

- Add `rental_contract_terms` Html field on `res.company`, exposed in Rental Settings as a rich-text editor
- Add `action_print_rental_contract()` on `sale.order`: hard-blocks with `UserError` if `rental_status` is not in `('pickup', 'return', 'returned')` — contract is only printable once the order is confirmed and reserved
- Add "Print Contract" button on the rental order form (visible when `is_rental_order = True`)
- New QWeb report template `report_rental_contract_document` with dedicated layout (see design)
- New `ir.actions.report` record ("Rental Contract") bound to `sale.order` — separate from the existing Pickup and Return Receipt
- Contract reference uses the sale order name for now (`doc.name`)

## Capabilities

### New Capabilities
- `rental-contract-print`: Print a rental agreement from a confirmed rental order, with company-configured rich-text terms, rental item table, deposit table, financial summary, and customer/staff signature lines. Blocked if the order has not yet reached pickup-ready state.

### Modified Capabilities

## Impact

- **Models**: `res.company` (new `rental_contract_terms` Html field), `res.config.settings` (new related field), `sale.order` (new `action_print_rental_contract` method)
- **Views**: Rental order form view (new button), Rental Settings form (new terms section)
- **Reports**: New `report/rental_contract_templates.xml`; new `ir.actions.report` record in `rental_report_views.xml`
- **Manifest**: `rental_contract_templates.xml` added to data list
- **No changes** to existing Pickup and Return Receipt, deposit logic, or pickup wizard
