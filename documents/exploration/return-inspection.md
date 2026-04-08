# Return Inspection & Damage Location Flow

**Status: No Decision Yet**
**Date: 2025-04-07**

---

## Problem

When customers return rental products, items go directly back to warehouse stock and become immediately rentable. Users want to inspect products before making them available again, and damaged products should be held separately.

## Proposed Flow

### Return Wizard (modified)

Three-way condition per item at return:

| Condition       | Destination          | Side Effects         |
|-----------------|----------------------|----------------------|
| **Damaged**     | Damage Location      | + damage fee + log   |
| **Good (Normal)** | Warehouse Stock   | Immediately rentable |
| **Inspect**     | Inspection Location  | Blocked from rental  |

### Release from Inspection Wizard (new)

Opened from the rental order when status = `inspect`. Per-item result:

| Result          | Destination          | Side Effects         |
|-----------------|----------------------|----------------------|
| **No Damage**   | Warehouse Stock      | Rentable             |
| **Damaged**     | Damage Location      | + damage fee + log   |

### Damage Disposition

Out of scope for custom development. Use Odoo standard:
- **Repair** → internal transfer: Damage Location → Warehouse Stock
- **Scrap** → standard scrap operation from Damage Location

## Stock Locations

| Location            | Rentable? | Purpose                      |
|---------------------|-----------|------------------------------|
| Warehouse Stock     | Yes       | Available for rental         |
| Rental Location     | No        | Currently rented out (existing) |
| Inspection Location | No        | Returned, pending deep check |
| Damage Location     | No        | Confirmed damaged            |

New locations (Inspection, Damage) created per company, similar to existing Rental Location.

## Rental Order Status Flow

```
draft → sent → pickup → return → inspect → returned
                                    ▲
                                    │ new state
                                    │ (only if any item sent to inspection)
```

- **inspect**: all qty returned but some items still in inspection location
- **returned**: all items released from inspection

If no items sent to inspection, order goes directly from `return` → `returned` (current behavior preserved).

## UX Summary

### Return Wizard (existing, modified)

```
┌───────────────────────────────────────────────────┐
│ Product      │ Lot/Serial │ Qty │ Condition      │
├───────────────────────────────────────────────────┤
│ Excavator A  │ SN-001     │  1  │ [Good       ▼] │
│ Drill B      │ SN-042     │  1  │ [Inspect    ▼] │
│ Drill B      │ SN-043     │  1  │ [Damaged    ▼] │
└───────────────────────────────────────────────────┘
```

Damage fee/reason fields shown only when condition = Damaged.

### Release Wizard (new)

```
┌───────────────────────────────────────────────────┐
│ Product      │ Lot/Serial │ Result               │
├───────────────────────────────────────────────────┤
│ Drill B      │ SN-042     │ [No Damage     ▼]   │
└───────────────────────────────────────────────────┘
```

Damage fee/reason fields shown only when result = Damaged.

## Scope Boundary

### In Scope (custom)

1. Return wizard: 3-way condition (Damaged / Good / Inspect)
2. Release wizard: 2-way result (No Damage / Damaged)
3. New stock locations: Inspection Location, Damage Location (per company)
4. Rental status: add `inspect` state
5. Damaged products route to Damage Location (both at return and after inspection)

### Out of Scope (use Odoo standard)

- Damage → Repair → Stock: internal transfer
- Damage → Scrap: standard scrap operation
- Inspection queue / dashboard (can filter orders by inspect status)

## Open Questions

- None captured yet — pending decision to proceed.
