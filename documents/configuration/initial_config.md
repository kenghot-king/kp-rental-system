# Rental Property System — Initial Configuration Guide

This guide walks through the steps required to configure Odoo 19 CE with the `ggg_rental` module for property/equipment rental operations. Follow sections in order.

---

## 1. Invoicing Settings

### 1.1 Fiscal Localization
**Path:** Accounting → Configuration → Settings → Fiscal Localization

| Setting | Value |
|---|---|
| Package | Thailand |

Install the Thailand localization package to get Thai-specific chart of accounts and tax templates.

### 1.2 Taxes
**Path:** Accounting → Configuration → Taxes → New

Create the following taxes manually (Thailand localization does not auto-create include-type taxes):

#### Output 7% include

| Field | Value |
|---|---|
| Tax Name | `Output 7% include` |
| Tax Type | Sales |
| Tax Computation | Percentage of Price |
| Amount | `7.00` % |
| Label on Invoices | `Output VAT 7% (include)` |
| Tax Group | `VAT 7%` |
| Price Included | ✅ Yes |
| Include in Base Amount | ✅ Yes |
| **Invoice — Tax account** | `Output VAT` |
| **Credit Note — Tax account** | `Output VAT` |

#### Input vat 7% include

| Field | Value |
|---|---|
| Tax Name | `Input vat 7% include` |
| Tax Type | Purchases |
| Tax Computation | Percentage of Price |
| Amount | `7.00` % |
| Label on Invoices | `Input VAT 7% include` |
| Tax Group | `VAT 7%` |
| Price Included | ✅ Yes |
| Include in Base Amount | ✅ Yes |
| **Invoice — Tax account** | `Input VAT` |
| **Credit Note — Tax account** | `Input VAT` |

> **Note:** "Price Included" means the tax is already embedded in the product price — the customer sees the gross price directly. Both taxes use `VAT 7%` as their tax group. Apply Output tax on sales products; Input tax on purchased/cost products.

---

## 2. Inventory Settings

### 2.1 Traceability
**Path:** Inventory → Configuration → Settings → Traceability

| Setting | Value |
|---|---|
| Lots & Serial Numbers | ✅ Enabled |

Required for tracking individual rental items by serial number (deposits per unit, damage per unit, return matching).

### 2.2 Warehouse
**Path:** Inventory → Configuration → Settings → Warehouse

| Setting | Value |
|---|---|
| Storage Locations | ✅ Enabled |

Required to support separate internal locations for damage and inspection.

---

## 3. Stock Locations

### 3.1 Configured Locations
The following locations have been created and assigned to the company:

#### Suspend Location (parent container)

| Field | Value |
|---|---|
| Name | `Suspend` |
| Full Path | `Suspend` |
| Location Type | Virtual |
| Parent | *(none — top level)* |
| Warehouse | *(none)* |

> **Why a separate top-level parent?** Damage and Inspection units are physically held by the company but must NOT count toward "Free to Use" / bookable quantity at the warehouse scope. By parenting them under `Suspend` (outside the `WH` tree), warehouse-scoped views (Stock report, sales/rental availability, website in-stock indicator) automatically exclude them. They remain `Internal` so valuation reports still see them.

#### Rental Location

| Field | Value |
|---|---|
| Name | `Rental` |
| Full Path | `Customers/Rental` |
| Location Type | Internal |
| Parent | `Customers` |
| Warehouse | My Company |
| Is Valued (Internal) | Yes |

#### Damage Location (id: 15)

| Field | Value |
|---|---|
| Name | `Damage` |
| Full Path | `Suspend/Damage` |
| Location Type | Internal |
| Parent | `Suspend` |
| Warehouse | *(none — outside WH)* |
| Active | Yes |
| Is Valued (Internal) | Yes |
| Replenishments | No |
| Removal Strategy | *(none)* |
| Barcode | *(none)* |
| Inventory Frequency | 0 (disabled) |
| Created | 2026-04-17 |

#### Inspection Location (id: 16)

| Field | Value |
|---|---|
| Name | `Inspection` |
| Full Path | `Suspend/Inspection` |
| Location Type | Internal |
| Parent | `Suspend` |
| Warehouse | *(none — outside WH)* |
| Active | Yes |
| Is Valued (Internal) | Yes |
| Replenishments | No |
| Removal Strategy | *(none)* |
| Barcode | *(none)* |
| Inventory Frequency | 0 (disabled) |
| Created | 2026-04-17 |

Resulting structure:

```
(top level)
├── WH (Virtual)
│   └── WH/Stock              [Internal]   ← bookable
├── Customers
│   └── Customers/Rental      [Internal]   ← out on rent
└── Suspend (Virtual)
    ├── Suspend/Damage        [Internal]   ← excluded from bookable
    └── Suspend/Inspection    [Internal]   ← excluded from bookable
```

Verify these exist at:
**Inventory → Configuration → Locations** (enable developer mode to see all)

### 3.2 Manual Locations (Optional)
You may create additional sub-locations under Damage or Inspection for finer tracking (e.g., "Damage / Workshop", "Inspection / Pending Photo"). Keep them under the `Suspend` tree so they inherit the same bookable-exclusion behavior.

---

## 4. Rental Settings

**Path:** Rental → Configuration → Settings

### 4.1 Locations
Assign the locations to the company (already configured):

| Field | Location | Path |
|---|---|---|
| Rental Location | Rental | `Customers/Rental` |
| Damage Location | Damage | `Suspend/Damage` |
| Inspection Location | Inspection | `Suspend/Inspection` |

> **Note:** Return workflow will raise an error if Damage or Inspection location is not configured when the operator selects those conditions.

> **Bookable invariant:** Damage and Inspection live under the top-level `Suspend` virtual location (not under `WH`). This ensures units in those locations are excluded from "Free to Use" / availability checks at warehouse scope while remaining on the company's books for valuation. See section 3.1.

### 4.2 Delay Costs
Default costs applied when a customer returns items late.

| Field | Recommended Value | Description |
|---|---|---|
| Per Hour | (your rate) | Charge per hour of delay |
| Per Day | (your rate) | Charge per day of delay |
| Apply after | `2` hours | Grace period before delay charges begin |
| Extra Time Product | `Rental Delay` (service) | Service product invoiced for delay charges |

### 4.3 Damage Product
Service product invoiced when items are returned damaged or flagged for inspection.

| Field | Value |
|---|---|
| Damage Product | `Rental Damage` (service, `default_code = DAMAGE`) |

> If not configured, the system auto-creates a product named "Rental Damage" on first use.

### 4.4 Deposit
| Field | Recommended Value | Description |
|---|---|---|
| Deposit Product | `Rental Deposit` (service, `is_rental_deposit = True`) | Product used for auto-created deposit lines |
| Auto Refund Deposit | ✅ Enabled | Automatically register refund payment when deposit credit note is created |

> The deposit product must have `is_rental_deposit = True` set on the product form. Deposit sync will fail with a UserError if this is not configured.

### 4.5 Pickup Requirements
| Field | Recommended Value | Description |
|---|---|---|
| Require Payment Before Pickup | (your policy) | Blocks pickup if any posted invoice is unpaid |

### 4.6 Rental Contract Terms
Enter the terms and conditions to print on rental contracts (rich text editor).

---

## 5. Service Products Setup

Create the following service products before going live. Some are auto-created on first use but it is better practice to create them manually.

### 5.1 Extra Time / Delay Product
| Field | Value |
|---|---|
| Name | `Rental Delay` |
| Type | Service |
| Internal Reference | `RENTAL` |
| Sales Price | 0.00 (overridden per-order) |

### 5.2 Damage Product
| Field | Value |
|---|---|
| Name | `Rental Damage Fee` |
| Type | Service |
| Internal Reference | `DAMAGE` |
| Sales Price | `1.00` (overridden per-return) |
| Unit of Measure | Units |
| Customer Taxes | `7%` (sales, price excluded) |
| Is Rental Deposit | No |

### 5.3 Rental Deposit Product
| Field | Value |
|---|---|
| Name | `Security Deposit` |
| Type | Service |
| Internal Reference | *(none)* |
| Sales Price | `0.00` (set per-product via Deposit Price) |
| Unit of Measure | Units |
| Customer Taxes | *(none)* |
| Is Rental Deposit | ✅ Yes |

---

## 6. Rental Products Setup

For each product offered for rent:

### 6.1 Product Form — General Tab
| Field | Value |
|---|---|
| Product Type | Storable (for serial tracking) or Consumable |
| Can be Rented | ✅ Enabled |
| Tracking | By Unique Serial Number (recommended for high-value items) |

### 6.2 Product Form — Rental Tab
| Field | Value |
|---|---|
| Extra Hourly Cost | (leave blank to use company default) |
| Extra Daily Cost | (leave blank to use company default) |
| Deposit Price | Security deposit amount per unit |

### 6.3 Pricing Rules
Add rental pricing periods on the product's Rental tab:

| Period | Example Price |
|---|---|
| Hourly | - |
| Daily | - |
| Weekly | - |
| Monthly | - |

> **Note:** Nightly periods cannot be mixed with other period types on the same product.

---

## 6.4 Before Importing Serials

After product master data is set up, use the **Import Serials** button on the Rental Products list to bulk-load serial numbers (one per physical unit) into stock.

### Prerequisites

**Set `Cost Price` (standard_price) on every rental product before importing.**

When a serial is imported, Odoo runs a standard inventory adjustment (`_apply_inventory()`), which books the unit to *Stock Valuation* and credits the *Inventory Adjustment* account at the product's current `standard_price`. If `standard_price = 0` at import time, the serial and quant are still created but no valuation entry is posted — re-running the import later will not fix the valuation of already-created quants.

> **Path to set cost:** Rental → Products → [Product] → Purchase tab → Cost

### Import Format

Download the template via **Rental → Products → ⚙ → Download Serial Template**. Fill in one row per physical unit:

| Column | Description |
|---|---|
| `sap_article_code` | Must match the product's SAP Article Code exactly |
| `serial_number` | Unique serial identifier for the unit |

### Import Behavior

- Each serial lands at **WH/Stock** (the active company's default warehouse `lot_stock_id`) with `quantity = 1.0`
- Duplicate serials (already in DB or repeated in the same CSV) are **warned and skipped** — the import does not abort
- Products that are not rental, not storable, not serial-tracked, or have multiple variants are rejected per row with a clear error message
- The import is **additive only** — existing serials are never modified or deleted

### One-Time Accountant Journal Entry

Since Odoo is now the system of record for fleet valuation, the accountant should record a one-time journal entry to retire any prior fleet asset row from the legacy accounting system:

| Account | Debit | Credit | Memo |
|---|---|---|---|
| Fleet Asset (old system) | — | Total fleet cost | Transfer fleet to Odoo |
| Inventory Adjustment | Total fleet cost | — | Fleet import via serial CSV |

> This offsets the credit that Odoo's `_apply_inventory()` posted to the Inventory Adjustment account, and closes out the fleet asset in the prior system. Coordinate with the accountant on the exact accounts and amounts before posting.

---

## 7. Warehouse Configuration

Verify the default warehouse has a stock location (`lot_stock_id`) configured. This is the destination used when items are returned in **Good** condition.

**Path:** Inventory → Configuration → Warehouses → [Warehouse] → Technical tab

| Field | Required |
|---|---|
| Short Name | (set to company short code) |
| Main Location | Confirmed (auto-set by Odoo) |

---

## 8. Payment Methods (Optional)

The module ships with default payment journal entries. Verify or update in:
**Accounting → Configuration → Journals**

Default journals created on install:
- Cash
- VISA
- MASTER
- QR PromptPay
- Transfer

---

## 9. User Access

**Path:** Settings → Users & Companies → Users

Assign users to the appropriate group:

| Group | Access Level |
|---|---|
| Sales / User | Process pickups, returns, view damage logs |
| Sales / Administrator | Configure rental settings, manage all records |

---

## 10. Post-Install Verification Checklist

- [ ] Thailand Fiscal Localization package installed
- [ ] Output VAT 7% (include) tax created — type: Sales, price included
- [ ] Input VAT 7% (include) tax created — type: Purchases, price included
- [ ] Lots & Serial Numbers enabled in Inventory settings
- [ ] Storage Locations enabled in Inventory settings
- [ ] Rental, Damage, Inspection locations exist and are assigned in Rental Settings
- [ ] Damage Product configured in Rental Settings → Damage
- [ ] Deposit Product configured in Rental Settings → Deposit
- [ ] Extra Time Product configured in Rental Settings → Delay Costs
- [ ] At least one rentable product created with pricing rules
- [ ] Standard price (`Cost Price`) set on all rental products before importing serials
- [ ] Default warehouse has `lot_stock_id` configured
- [ ] Users assigned to correct sales group

---

## 11. Return Condition Routing Reference

When an operator processes a return in the Return Wizard, the item is routed based on the selected condition:

| Condition | Destination | Fee Charged | Error if Location Missing |
|---|---|---|---|
| Good | Warehouse Main Stock (`lot_stock_id`) | No | No |
| Damaged | Damage Location | Yes (at return time) | Yes |
| Inspect | Inspection Location | Optional (fee can be 0) | Yes |

After items land in Damage or Inspection locations, staff use standard Inventory transfers to move them forward (repair, scrap, return to stock, etc.).
