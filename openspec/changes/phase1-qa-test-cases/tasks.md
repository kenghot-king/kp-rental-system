## 1. Generate QA Test Case Documents

- [x] 1.1 Create `documents/QA/phase1/` directory
- [x] 1.2 Generate `documents/QA/phase1/tc-rental-order.md` from specs/tc-rental-order
- [x] 1.3 Generate `documents/QA/phase1/tc-pricing.md` from specs/tc-pricing
- [x] 1.4 Generate `documents/QA/phase1/tc-pickup-return.md` from specs/tc-pickup-return
- [x] 1.5 Generate `documents/QA/phase1/tc-late-fees.md` from specs/tc-late-fees
- [x] 1.6 Generate `documents/QA/phase1/tc-damage-assessment.md` from specs/tc-damage-assessment
- [x] 1.7 Generate `documents/QA/phase1/tc-deposit.md` from specs/tc-deposit
- [x] 1.8 Generate `documents/QA/phase1/tc-stock-integration.md` from specs/tc-stock-integration
- [x] 1.9 Generate `documents/QA/phase1/tc-reporting-views.md` from specs/tc-reporting-views

## 2. Test Environment Setup

- [ ] 2.1 Prepare test data: 2 rental products (1 serial-tracked, 1 non-tracked), pricing rules (daily + weekly), deposit product, company settings configured
- [ ] 2.2 Create test users: Salesman, Manager, System Admin

## 2. Rental Order Tests (TC-RO-001 to TC-RO-017)

- [ ] 2.1 Execute TC-RO-001 to TC-RO-004: Order creation and date validation
- [ ] 2.2 Execute TC-RO-005 to TC-RO-010: Status transitions (draft → sent → pickup → return → returned, partial scenarios)
- [ ] 2.3 Execute TC-RO-011 to TC-RO-012: Cancel order scenarios
- [ ] 2.4 Execute TC-RO-013 to TC-RO-015: Late detection
- [ ] 2.5 Execute TC-RO-016 to TC-RO-017: Price update on date change

## 3. Pricing Tests (TC-PR-001 to TC-PR-014)

- [ ] 3.1 Execute TC-PR-001 to TC-PR-003: Single-period pricing
- [ ] 3.2 Execute TC-PR-004 to TC-PR-006: Best pricing selection
- [ ] 3.3 Execute TC-PR-007 to TC-PR-008: Pricelist-specific pricing
- [ ] 3.4 Execute TC-PR-009 to TC-PR-010: Variant-specific pricing
- [ ] 3.5 Execute TC-PR-011: Overnight pricing
- [ ] 3.6 Execute TC-PR-012 to TC-PR-014: Display price and recurrence config

## 4. Pickup & Return Tests (TC-PK-001 to TC-RT-008)

- [ ] 4.1 Execute TC-PK-001 to TC-PK-003: Bulk product pickup
- [ ] 4.2 Execute TC-PK-004 to TC-PK-007: Serial-tracked pickup
- [ ] 4.3 Execute TC-RT-001 to TC-RT-003: Bulk product return
- [ ] 4.4 Execute TC-RT-004 to TC-RT-008: Serial-tracked return and chatter logging

## 5. Late Fee Tests (TC-LF-001 to TC-LF-009)

- [ ] 5.1 Execute TC-LF-001 to TC-LF-006: Late fee calculation scenarios
- [ ] 5.2 Execute TC-LF-007 to TC-LF-009: Product-level override and grace period config

## 6. Damage Assessment Tests (TC-DA-001 to TC-DA-014)

- [ ] 6.1 Execute TC-DA-001 to TC-DA-005: Condition assessment UI
- [ ] 6.2 Execute TC-DA-006 to TC-DA-008: Damage fee SO line creation
- [ ] 6.3 Execute TC-DA-009 to TC-DA-011: Damage log records and serial split
- [ ] 6.4 Execute TC-DA-012 to TC-DA-014: Damage history on serial and settings

## 7. Deposit Tests (TC-DP-001 to TC-DP-010)

- [ ] 7.1 Execute TC-DP-001: Deposit product setup
- [ ] 7.2 Execute TC-DP-002 to TC-DP-004: Split invoicing
- [ ] 7.3 Execute TC-DP-005 to TC-DP-007: Deposit credit note on return (full, partial, second return)
- [ ] 7.4 Execute TC-DP-008 to TC-DP-010: Auto-refund setting

## 8. Stock Integration Tests (TC-ST-001 to TC-ST-011)

- [ ] 8.1 Execute TC-ST-001 to TC-ST-002: Delivery move and rental location
- [ ] 8.2 Execute TC-ST-003 to TC-ST-004: Pickup stock validation
- [ ] 8.3 Execute TC-ST-005 to TC-ST-007: Return stock moves
- [ ] 8.4 Execute TC-ST-008 to TC-ST-011: Stock move visibility and qty in rent

## 9. Reporting & Views Tests (TC-RP-001 to TC-RP-017)

- [ ] 9.1 Execute TC-RP-001 to TC-RP-005: Rental analysis report
- [ ] 9.2 Execute TC-RP-006 to TC-RP-009: Gantt schedule view
- [ ] 9.3 Execute TC-RP-010 to TC-RP-013: List view and product catalog
- [ ] 9.4 Execute TC-RP-014 to TC-RP-017: Access control
