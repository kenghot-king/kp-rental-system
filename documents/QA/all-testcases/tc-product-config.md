# Test Cases: Product & Rental Configuration

> Module: `ggg_rental` | Last updated: 2026-04-23

## Preconditions

- User with Product Manager or Rental Manager role
- Company settings accessible

---

## 1. Rental Product Setup

### TC-PC-001: Enable rent_ok on product

| Field | Value |
|-------|-------|
| **Precondition** | Standard storable product |
| **Steps** | 1. Open product form<br>2. Check "Can be Rented" (`rent_ok = True`)<br>3. Save |
| **Expected** | Product appears in rental product lists; Pricing tab visible |
| **Result** | |

### TC-PC-002: Rental combo validates all items are rent_ok

| Field | Value |
|-------|-------|
| **Precondition** | Combo product with `rent_ok = True`; one combo item has `rent_ok = False` |
| **Steps** | 1. Try to save the combo product |
| **Expected** | Validation error: all combo items must be rentable |
| **Result** | |

### TC-PC-003: Rental product restricted to single UOM

| Field | Value |
|-------|-------|
| **Precondition** | Rental product |
| **Steps** | 1. Check `_has_multiple_uoms()` on rental product |
| **Expected** | Returns False; product cannot have multiple UOMs |
| **Result** | |

### TC-PC-004: qty_in_rent computed from variants

| Field | Value |
|-------|-------|
| **Precondition** | Product template with 2 variants; 3 units of V1 rented and 1 unit of V2 rented |
| **Steps** | 1. Check `qty_in_rent` on product template |
| **Expected** | `qty_in_rent = 4` |
| **Result** | |

---

## 2. Company Settings

### TC-PC-005: Set rental start date padding

| Field | Value |
|-------|-------|
| **Precondition** | Rental Configuration settings |
| **Steps** | 1. Set rental start offset (e.g., +1 hour padding)<br>2. Create new order |
| **Expected** | Default start date = now + configured offset |
| **Result** | |

### TC-PC-006: Toggle require_payment_before_pickup

| Field | Value |
|-------|-------|
| **Precondition** | Configuration settings |
| **Steps** | 1. Enable `require_payment_before_pickup`<br>2. Create order; do not pay; try pickup |
| **Expected** | Pickup blocked with payment required error |
| **Result** | |

### TC-PC-007: Toggle deposit_auto_refund setting

| Field | Value |
|-------|-------|
| **Precondition** | Configuration settings |
| **Steps** | 1. Toggle `deposit_auto_refund` on/off<br>2. Verify behavior on return |
| **Expected** | On: auto-creates payment on return; Off: credit note only |
| **Result** | |

### TC-PC-008: Configure rental location

| Field | Value |
|-------|-------|
| **Precondition** | Settings |
| **Steps** | 1. Set `rental_loc_id` to a stock location<br>2. Pick up items |
| **Expected** | Delivery moves go to the configured rental location |
| **Result** | |

### TC-PC-009: Configure damage and inspection locations

| Field | Value |
|-------|-------|
| **Precondition** | Settings |
| **Steps** | 1. Set `damage_loc_id` and `inspection_loc_id`<br>2. Return items as damaged/inspect |
| **Expected** | Items routed to respective configured locations |
| **Result** | |

---

## 3. Pricelist Configuration

### TC-PC-010: Create rental pricelist

| Field | Value |
|-------|-------|
| **Precondition** | Pricelists enabled in sales settings |
| **Steps** | 1. Create pricelist for rental customers<br>2. Set discount on pricing rules |
| **Expected** | Pricelist saved and selectable on rental orders |
| **Result** | |

### TC-PC-011: Pricelist-specific pricing overrides base

| Field | Value |
|-------|-------|
| **Precondition** | Product with base price 500/day; pricelist price 400/day |
| **Steps** | 1. Create order with the pricelist<br>2. Add product |
| **Expected** | Price = 400/day (pricelist rule wins) |
| **Result** | |

---

## 4. Product Copy

### TC-PC-012: Copy product preserves pricing rules

| Field | Value |
|-------|-------|
| **Precondition** | Product with 3 pricing rules |
| **Steps** | 1. Duplicate the product |
| **Expected** | Copied product has 3 pricing rules (copy=False workaround via custom copy()) |
| **Result** | |

### TC-PC-013: Copy product maps variant pricing to new variants

| Field | Value |
|-------|-------|
| **Precondition** | Product with variant-specific pricing |
| **Steps** | 1. Duplicate product |
| **Expected** | Variant-specific pricing on copy references the NEW product's variants |
| **Result** | |

---

## 5. Rental Report on Product Configurator

### TC-PC-014: Product configurator shows rental pricing info

| Field | Value |
|-------|-------|
| **Precondition** | Rental product with daily pricing |
| **Steps** | 1. Open product selector in rental order (configurator view) |
| **Expected** | Product tile shows "X / Day" pricing summary |
| **Result** | |

### TC-PC-015: Non-rental products excluded from rental product list

| Field | Value |
|-------|-------|
| **Precondition** | Mix of rental and non-rental products |
| **Steps** | 1. Open Rental > Products catalog |
| **Expected** | Only products with `rent_ok=True` listed |
| **Result** | |
