# Rental Process Workflow

This document outlines the standard rental process workflow, including validation, invoicing, deposit handling, return inspection, and damage assessment flows.

## High-Level Lifecycle Flow

```mermaid
stateDiagram-v2
    direction LR
    
    [*] --> Draft: Create Quote
    Draft --> Sent: Send Quote
    Draft --> Pickup: Confirm Order\n(Validation)
    Sent --> Pickup: Confirm Order\n(Validation)
    
    Pickup --> Return: Validate Pickup\n(Items given to Customer)
    
    Return --> Inspect: Validate Return\n(Needs Inspection/Damaged)
    Return --> Returned: Validate Return\n(All Items Good)
    
    Inspect --> Returned: Complete Inspection\n(Release/Scrap/Repair)
    
    Returned --> [*]
```

## State Descriptions & Validation Actions

| State | Description & Validation Actions | Stock Location Status |
|---|---|---|
| **Draft** | Initial quotation created for the customer. Pricing rules (daily, weekly, variant) are applied based on the duration. | Pre-allocation |
| **Sent** | Quotation has been sent to the customer for review. | Pre-allocation |
| **Pickup** | **Validation:** Order is confirmed. <br>**Invoicing:** Invoices and deposit invoices are generated and Payments are collected. <br>Items are awaiting pickup by the customer or delivery. | Warehouse Stock |
| **Return** | **Validation:** Items have been validated as picked up and are currently with the customer. | Rental Location |
| **Inspect** | **Validation:** Items returned require deep evaluation. They have been routed to the Inspection or Damage Location. | Inspection Location / Damage Location |
| **Returned** | **Validation:** All items have been fully returned, inspected, and any applicable deposits have been refunded. | Warehouse Stock / Damage Location |

---

## Invoicing & Deposit Management

Handling payments securely and accurately is a critical part of the rental validation process.

### Split Invoicing on Order Confirmation
When an order is confirmed, the system separates standard rental charges from deposit charges:
- **Mixed Orders:** Generate two separate invoices (one invoice specifically for the deposit only, and a second invoice for the rental lines).
- **Rental-Only Orders:** Generate a single invoice for the rental cost.
- **Deposit-Only Orders:** Generate a single invoice for the deposit.

### Deposit Refunds on Return

As items are returned via the Return Wizard, the previously invoiced deposits are processed for refund. 

```mermaid
sequenceDiagram
    participant Customer
    participant Order as Rental Order
    participant Invoicing
    participant Payment

    Customer->>Order: Returns Item(s)
    Order->>Invoicing: Calculates Returned Quantity
    Invoicing->>Invoicing: Generates Credit Note
    
    alt Full Return
        Invoicing-->>Customer: Full Deposit Credited
    else Partial Return
        Invoicing-->>Customer: Proportional Deposit Credited
    end
    
    alt Auto Refund Enabled
        Invoicing->>Payment: Registers Payment Automatically
    else Auto Refund Disabled
        Invoicing-->>Payment: Awaits Manual Staff Processing
    end
```

**Partial Returns:** If a customer returns only a subset of their rented items initially, a proportional credit note is generated based on the quantity returned. Additional credit notes are generated for downstream partial returns until the full deposit is refunded.

### Checking Reverse Invoices in Reporting > By Item

The By Item report lists the product lines of customer invoices and credit notes (RINV), so accounting can check the reverse invoice for an order.

- **Negative amounts:** Subtotal and Tax are negative on credit note lines, so totals are net. Unit Price and Quantity stay positive, as printed on the document.
- **Totals in a long list:** The total at the bottom of the ungrouped list covers only the rows on the current page, or the selected rows. Check the row counter at the top right. When the list runs over more than one page, group the lines to get a total for each group.
- **Grouped rows:** Rely on Subtotal and Tax in a group row. Quantity and Unit Price in a group row are plain sums that ignore credit notes, so they are not meaningful.
- **Order:** Shows the sale order on each line. Group by Order to see an invoice next to its reversal.
- **Reversal Of:** Shows the original invoice on a credit note.
- **Posted by default:** The report opens on posted documents. Remove the Posted filter to see draft and cancelled documents, which then count towards the totals.
- **Filters:** Use Invoices, Credit Notes and Reversed to narrow the list. An unpaid invoice that has been fully credited has the status `Reversed`.
- **Held deposits:** A deposit held on a card and later released or forfeited has no credit note, so no RINV line appears for it. This is expected.

---

## Return & Inspection Routing

When items are validated during return, the return wizard dictates the inventory routing of each specific item based on its exact condition.

```mermaid
flowchart TD
    Customer[Customer / Rental Location] -->|Return Wizard| Condition{Condition at Return?}
    
    Condition -->|Good / Normal| Stock[Warehouse Stock]
    Condition -->|Inspect| InspLoc[Inspection Location]
    Condition -->|Damaged| DamLoc[Damage Location]
    
    InspLoc -->|Release Wizard| Result{Inspection Result?}
    Result -->|No Damage| Stock
    Result -->|Damaged| DamLoc
    
    Stock -->|Ready| Rentable((Available for Rent))
    DamLoc -->|Requires Action| RepairScrap((Repair or Scrap))
```

### Routing Rules & Inventory Flow

1. **Good Condition:** 
   - Routed directly back to **Warehouse Stock**.
   - Made immediately available and rentable for future orders.
   - If all items in an order are returned in good condition, the order state skips `Inspect` and jumps directly to `Returned`.
2. **Inspect:** 
   - Temporarily routed to the **Inspection Location** pending a deep validation check.
   - These items are blocked from showing as rentable.
   - Uses the specific Release Wizard to finalize the condition (No Damage vs. Damaged).
   - If any item in an order requires inspection, the order status moves to `Inspect`.
3. **Damaged:** 
   - Routed to the **Damage Location** for quarantine.
   - These items are flagged to generate a damage fee + log on the order.
   - Resolving items from the Damage Location happens outside of the custom rental flow via standard Odoo Repair or Scrap operations.
