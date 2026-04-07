## Context

The ggg_rental module implements a full rental workflow on Odoo 19 CE: product setup with multi-period pricing, rental order management, pickup/return wizards with serial number tracking, late fee and damage fee processing, deposit handling with split invoicing and auto-refund, and rental analysis reporting. QA needs structured test cases before go-live.

## Goals / Non-Goals

**Goals:**
- Cover all Phase 1 DONE and PARTIAL features with testable scenarios
- Each test case has clear preconditions, steps, and expected results
- Group test cases by functional area for easy assignment to QA team
- Include edge cases and error scenarios, not just happy paths

**Non-Goals:**
- Automated test scripts (these are manual QA test cases)
- Test cases for DEFERRED/Next Phase items (#6, #10, #12, #13, #29, #34, #35, #41, #49-#54)
- Performance or load testing
- Test cases for features not yet implemented (#19-#22 payment refs, #16 quotation PDF, #23 document templates, #40 SAP export)

## Decisions

### Test case format
Each test case uses: ID, title, preconditions, steps, expected result. Grouped by capability area matching BRD sections. This is standard QA format that can be imported into any test management tool.

### Coverage scope
Focus on what's actually implemented and testable in the current codebase. PARTIAL items get test cases for the working parts only, with notes on what's not yet testable.

### Test data assumptions
Test cases assume a demo environment with:
- At least 2 rental products (1 serial-tracked, 1 non-tracked)
- Pricing rules configured (daily, weekly minimum)
- A deposit product configured
- Company rental settings configured (late fees, grace period, damage product)

## Risks / Trade-offs

- **[Risk] Test cases may not cover all edge cases in pricing logic** → Mitigation: pricing tests include boundary cases (exact period, period + 1 hour, overnight)
- **[Risk] Serial tracking tests depend on stock availability** → Mitigation: preconditions specify required stock setup
