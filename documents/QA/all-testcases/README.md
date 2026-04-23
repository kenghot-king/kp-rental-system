# GGG Rental — Complete QA Test Cases

> Module: `ggg_rental` | Last updated: 2026-04-23

## Coverage

| File | Feature Area | Test Cases |
|------|-------------|------------|
| [tc-rental-order.md](tc-rental-order.md) | Rental Order Lifecycle | TC-RO-001 … TC-RO-030 |
| [tc-pricing.md](tc-pricing.md) | Pricing & Duration | TC-PR-001 … TC-PR-025 |
| [tc-deposit.md](tc-deposit.md) | Deposit Management | TC-DP-001 … TC-DP-025 |
| [tc-pickup-return.md](tc-pickup-return.md) | Pickup & Return Process | TC-PK-001 … TC-PK-030 |
| [tc-stock-serial.md](tc-stock-serial.md) | Stock & Serial Tracking | TC-ST-001 … TC-ST-020 |
| [tc-late-fees.md](tc-late-fees.md) | Late & Delay Fees | TC-LF-001 … TC-LF-015 |
| [tc-damage.md](tc-damage.md) | Damage Assessment & Fees | TC-DM-001 … TC-DM-015 |
| [tc-payment.md](tc-payment.md) | Payment Processing | TC-PM-001 … TC-PM-020 |
| [tc-reconciliation.md](tc-reconciliation.md) | Daily Reconciliation | TC-RC-001 … TC-RC-025 |
| [tc-product-config.md](tc-product-config.md) | Product Configuration | TC-PC-001 … TC-PC-015 |
| [tc-reporting.md](tc-reporting.md) | Reporting & Exports | TC-RP-001 … TC-RP-020 |

## Preconditions (Global)

- Odoo 19 CE with `ggg_rental` module installed
- Company: Thai locale, THB currency
- Rental locations configured (rental location, damage location, inspection location)
- At least one rental product with daily pricing
- Deposit product (`is_rental_deposit=True`) configured
- Users: Sales Manager, Salesman, Supervisor, Cashier roles available

## How to Use

1. Open a test case file by feature area
2. Execute each step in sequence
3. Record result in the **Result** column
4. Mark pass ✅ or fail ❌
