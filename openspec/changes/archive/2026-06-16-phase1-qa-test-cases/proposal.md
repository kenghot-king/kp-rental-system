## Why

Phase 1 of the rental module has 14 DONE and 6 PARTIAL items covering rental orders, pricing, pickup/return with serial tracking, late fees, damage assessment, deposits, and reporting. Before going live, QA needs a structured test plan covering all implemented features to validate correctness and catch regressions.

## What Changes

- Create comprehensive QA test cases covering all Phase 1 implemented features
- Organized by functional area matching the BRD sections
- Each test case has preconditions, steps, and expected results
- Covers happy paths, edge cases, and error scenarios
- Generate a standalone markdown file per spec capability and save to `documents/QA/phase1/`

## Capabilities

### New Capabilities
- `tc-rental-order`: Test cases for rental order creation, dates, status flow, and cancellation
- `tc-pricing`: Test cases for multi-period pricing, pricelist rules, and price recalculation
- `tc-pickup-return`: Test cases for pickup/return wizard with serial tracking
- `tc-late-fees`: Test cases for late fee calculation with grace period
- `tc-damage-assessment`: Test cases for damage condition, fees, and damage log
- `tc-deposit`: Test cases for deposit invoicing, split invoices, and credit note refund
- `tc-stock-integration`: Test cases for stock moves, rental location, and serial assignment
- `tc-reporting-views`: Test cases for rental analysis report, schedule (Gantt), and UI views

### Modified Capabilities
<!-- None -->

## Impact

- No code changes — this is a QA documentation deliverable
- Test cases reference existing models: sale.order, sale.order.line, product.template, product.pricing, rental.damage.log, stock.lot, account.payment
- Test cases cover wizard flows: rental.order.wizard (pickup/return)
