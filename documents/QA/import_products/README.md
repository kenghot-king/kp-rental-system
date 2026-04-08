# Import Products - Test Files

## Test Execution Order

### TC 5.1: Create New Products
**File:** `tc5.1_create_new_products.csv`

**Steps:**
1. Upgrade ggg_rental module
2. Go to Rental > Products
3. Click "Import Products" button
4. Upload `tc5.1_create_new_products.csv`

**Expected:**
- Result: created=8, updated=0, errors=0
- 8 new rental products created (IMP-PROJ-001 through IMP-MIC-001)
- All products have `rent_ok = True`
- Serial tracked products: PROJ-001, SND-001, CAM-001, LED-001, MIC-001
- Non-tracked products: TBL-001, CHR-001, SCR-001
- Pricing rules created per product (check Rental Prices tab)
- Products with empty pricing cells (e.g., TBL-001 has no "1 Hour" pricing)

---

### TC 5.2a: Update Products (Full)
**File:** `tc5.2_update_products.csv`
**Prerequisite:** Run TC 5.1 first

**Steps:**
1. Upload `tc5.2_update_products.csv`

**Expected:**
- Result: created=0, updated=3, errors=0
- IMP-PROJ-001: name changed to "Projector Epson X500 (Updated)", list_price=16000, extra_hourly=60, extra_daily=250
- IMP-PROJ-001: 1 Day=1200, 1 Week=5500, 1 Month=16000 (updated)
- IMP-PROJ-001: 1 Hour, 3 Hours, 1 Night, 2 Weeks **preserved** (columns missing from CSV)
- IMP-CHR-001: name changed to "Folding Chair Premium", list_price=1200, default_code=CHR-002
- IMP-CAM-001: pricing updated for 1 Day, 1 Week, 1 Month only; other periods preserved

### TC 5.2b: Update Pricing Only
**File:** `tc5.2_update_pricing_only.csv`
**Prerequisite:** Run TC 5.1 first

**Steps:**
1. Upload `tc5.2_update_pricing_only.csv`

**Expected:**
- Result: created=0, updated=3, errors=0
- Product fields (name, list_price, etc.) NOT modified
- IMP-SND-001: 1 Hour=600, 1 Day=2500, 1 Week=12000, 1 Month=35000 (updated/created)
- IMP-LED-001: 1 Hour **deleted** (empty cell), 1 Day=900, 1 Week=4000, 1 Month=12000
- IMP-MIC-001: pricing updated for listed periods; other periods preserved

---

### TC 5.3a: Edge Cases
**File:** `tc5.3_edge_cases.csv`

**Steps:**
1. Upload `tc5.3_edge_cases.csv`

**Expected:**
- Warnings: "Unknown column '6 Months' — skipped", "Unknown column 'InvalidCol' — skipped"
- Row 3 (missing SAP code): error "Row 3: missing sap_article_code — skipped"
- Row 4 (IMP-EDGE-002): "abc" pricing for 1 Day skipped (invalid float), 1 Week=2000 created
- Row 5 (IMP-EDGE-001 duplicate): updates the product created in row 2 (1 Day=600, 1 Week=2500)
- Row 6 (IMP-EDGE-003): 1 Day=800 created, 1 Week empty = no pricing created (new product)
- Result: created=3, updated=1, errors=1, warnings=2

### TC 5.3b: Merge Pricing with Deletes
**File:** `tc5.3_merge_pricing_delete.csv`
**Prerequisite:** Run TC 5.1 first

**Steps:**
1. Upload `tc5.3_merge_pricing_delete.csv`

**Expected:**
- Result: created=0, updated=2, errors=0
- IMP-PROJ-001:
  - 1 Hour: **deleted** (empty cell)
  - 3 Hours: **deleted** (empty cell)
  - 1 Day: updated to 1500
  - 1 Night: **deleted** (empty cell)
  - 1 Week: updated to 6000
  - 2 Weeks, 1 Month: **preserved** (columns not in CSV)
- IMP-SND-001:
  - 1 Hour: **deleted** (empty cell)
  - 3 Hours: **deleted** (empty cell)
  - 1 Day: **deleted** (empty cell)
  - 1 Night: updated to 3000
  - 1 Week: **deleted** (empty cell)
  - 2 Weeks, 1 Month: **preserved** (columns not in CSV)
