# KP Rental System — Solution Comparison

> Alternative Architecture Assessment
> Version: 1.0 | Date: 2026-03-23

---

## 1. Solution Overview

### Option A: Mendix + King Power POS + SAP (Existing Stack)

```mermaid
graph TB
    subgraph "Frontend"
        MX_WEB["Mendix Web App<br/>(Rental Management)"]
        MX_MOB["Mendix Mobile App<br/>(Staff / Pickup / Return)"]
    end

    subgraph "Mendix Platform"
        RENT["Rental Module<br/>(Low-Code)"]
        STK["Stock Module<br/>(Inventory Tracking)"]
    end

    subgraph "King Power POS (Existing)"
        POS["POS Terminal<br/>(Receipt & Payment)"]
        PAY["Payment Gateway<br/>(VISA/MC/QR)"]
        POS_SAP["POS → SAP<br/>(Existing Integration)"]
    end

    subgraph "SAP"
        FI["SAP FI<br/>Financial Accounting"]
        SD["SAP SD<br/>Sales & Distribution"]
        MM["SAP MM<br/>Material Management"]
    end

    MX_WEB --> RENT
    MX_MOB --> RENT
    RENT --> STK
    RENT -. "Staff manually enters<br/>rental doc # at POS" .-> POS
    POS --> PAY
    POS --> POS_SAP
    POS_SAP --> FI
    POS_SAP --> SD
```

### Option B: Odoo 19 CE (Current Approach)

```mermaid
graph TB
    subgraph "Frontend"
        OD_WEB["Odoo Web Client<br/>(Browser)"]
    end

    subgraph "Odoo 19 CE"
        RENT["ggg_rental<br/>(Rental Management)"]
        STK["stock<br/>(Warehouse & Inventory)"]
        ACC["account<br/>(Invoicing & Payments)"]
        L10N["l10n_th<br/>(Thai Localization)"]
    end

    subgraph "New Integration"
        BATCH["Batch Export<br/>(Daily Cron)"]
    end

    subgraph "SAP"
        FI["SAP FI<br/>Financial Accounting"]
        SD["SAP SD<br/>Sales & Distribution"]
    end

    OD_WEB --> RENT
    RENT --> STK
    RENT --> ACC
    ACC --> L10N
    ACC --> BATCH
    BATCH --> FI
    BATCH --> SD
```

---

## 2. Process Flow Comparison

### Option A: Mendix + POS Flow

```mermaid
sequenceDiagram
    actor Staff
    participant Mendix as Mendix App
    participant POS as KP POS
    participant SAP as SAP

    Note over Staff,SAP: === Create Rental ===
    Staff->>Mendix: Create rental order
    Mendix->>Mendix: Reserve stock
    Mendix->>Mendix: Generate rental doc number

    Note over Staff,SAP: === Pickup ===
    Staff->>Mendix: Scan S/N, confirm pickup
    Mendix->>Mendix: Update stock (→ Rented)

    Note over Staff,SAP: === Payment ===
    Staff->>POS: Create transaction
    Staff->>POS: Manually type rental doc #<br/>(no API from Mendix)
    POS->>POS: Print receipt
    POS->>SAP: Post FI document<br/>(existing integration)

    Note over Staff,SAP: === Return ===
    Staff->>Mendix: Scan S/N, confirm return
    Mendix->>Mendix: Update stock (→ Available)

    Note over Staff,SAP: === Deposit Refund ===
    Staff->>POS: Create refund transaction
    Staff->>POS: Manually type rental doc #<br/>(no API from Mendix)
    POS->>SAP: Post credit memo<br/>(existing integration)
```

### Option B: Odoo Flow

```mermaid
sequenceDiagram
    actor Staff
    participant Odoo as Odoo 19 CE
    participant SAP as SAP

    Note over Staff,SAP: === Create Rental ===
    Staff->>Odoo: Create rental order
    Odoo->>Odoo: Reserve stock

    Note over Staff,SAP: === Pickup ===
    Staff->>Odoo: Wizard: select S/N, confirm
    Odoo->>Odoo: Validate delivery picking

    Note over Staff,SAP: === Payment ===
    Staff->>Odoo: Create invoice → Register payment
    Odoo->>Odoo: Print receipt (PDF)

    Note over Staff,SAP: === Return ===
    Staff->>Odoo: Wizard: select S/N, confirm
    Odoo->>Odoo: Create return move
    Odoo->>Odoo: Auto-create deposit credit note
    Odoo->>Odoo: Auto-register refund payment

    Note over Staff,SAP: === SAP Sync ===
    Odoo->>SAP: Daily batch export<br/>(NEW integration)
```

---

## 3. Comparison Matrix

### 3.1 Functional Comparison

| Capability | Option A: Mendix + POS | Option B: Odoo |
|-----------|----------------------|----------------|
| Rental order management | Mendix (build from scratch) | Odoo (built from CLE AI engine) |
| Stock / S/N tracking | Mendix (build from scratch) | Odoo stock module (mature) |
| Payment processing | KP POS (existing) | Odoo payments (built-in) |
| Receipt printing | KP POS (existing) | Odoo PDF report |
| Invoice & credit note | KP POS → SAP | Odoo accounting |
| Deposit management | Manual via POS refund | Auto credit note on return |
| Late fee calculation | Mendix (build) | Odoo (built-in) |
| SAP integration | Existing POS→SAP (but requires significant SAP modification for rental transactions) | New (must build) |
| Reporting | Mendix dashboards (build) | Odoo built-in reports |


### 3.2 Technical Comparison

| Aspect | Option A: Mendix + POS | Option B: Odoo |
|--------|----------------------|----------------|
| Architecture | 3 systems (Mendix + POS + SAP) | 2 systems (Odoo + SAP) |
| Integration points | Mendix → POS (manual, no API) + POS ↔ SAP (existing, needs SAP modification) | Odoo → SAP (new) |
| Data ownership | Split (rental in Mendix, financial in POS/SAP) | Unified (all in Odoo) |
| Stock source of truth | Mendix | Odoo |
| Financial source of truth | SAP (via POS) | SAP (via Odoo batch) |
| Hosting | Mendix Cloud (SaaS) | On-prem Docker |
| Database | Mendix managed | PostgreSQL (self-managed) |
| Customization | Low-code (visual) | No-code (with CLE AI engine) |

### 3.3 Operational Comparison

| Factor | Option A: Mendix + POS | Option B: Odoo |
|--------|----------------------|----------------|
| Staff training | 2 systems (Mendix + POS) | 1 system (Odoo) |
| Daily workflow | Switch between Mendix & POS | Single screen |
| Receipt printing | POS (existing) | PDF report |
| Payment methods | POS (all existing methods) | Odoo (configured journals) |
| Data reconciliation | Mendix ↔ POS ↔ SAP | Odoo → SAP |

---

## 4. Pros & Cons

### Option A: Mendix + King Power POS + SAP

```
 ✅ PROS                                    ❌ CONS
 ─────────────────────────────────────────   ─────────────────────────────────────────
 SAP integration exists (POS→SAP)            3-system architecture (more complexity)
   but needs significant SAP modification     SAP modification required for rental
   for rental transaction types                  transaction types (deposit, refund, etc.)
 Payment methods already configured          Staff switches between 2 UIs
 Staff familiar with POS                     Mendix rental module: build from scratch
                                             Mendix stock tracking: build from scratch
 Mendix low-code = faster initial build      No API between Mendix & POS
 (but requirement is not clear)              (staff must manually enter rental doc #)
 Mendix Cloud = no infra to manage           Data split across systems
 POS handles offline scenarios               Mendix license cost (per user/month)
                                             Rental doc # ↔ POS transaction
                                               reconciliation needed
                                             Deposit refund is manual (POS refund)
                                             No unified reporting
                                               (rental in Mendix, financial in SAP)
```

### Option B: Odoo 19 CE (Current)

```
 ✅ PROS                                    ❌ CONS
 ─────────────────────────────────────────   ─────────────────────────────────────────
 Single system for all operations            Must build new SAP integration
 Rental module already built (ported EE)     Staff must learn new system (Odoo)
 Stock + S/N tracking mature & proven        On-prem infra to maintain
 Auto deposit refund on return               
 Unified data (rental + financial)
 Built-in reporting across all data
 Open source, no license fees
 Full customization control
 Single UI for staff
 Automated credit notes
```

---

## 5. Risk Assessment

```mermaid
graph LR
    subgraph "Option A Risks"
        A1["Mendix ↔ POS<br/>integration complexity"]
        A2["Data consistency<br/>across 3 systems"]
        A3["Mendix license<br/>cost escalation"]
        A4["Manual deposit<br/>refund errors"]
        A5["Reconciliation<br/>overhead"]
    end

    subgraph "Option B Risks"
        B1["SAP integration<br/>must be built"]
        B3["Staff retraining<br/>on Odoo"]
        B4["On-prem infra<br/>maintenance"]
    end

    style A1 fill:#FF9800,color:#fff
    style A2 fill:#f44336,color:#fff
    style A3 fill:#FF9800,color:#fff
    style A4 fill:#FF9800,color:#fff
    style A5 fill:#FF9800,color:#fff
    style B1 fill:#FF9800,color:#fff
    style B3 fill:#FFC107,color:#000
    style B4 fill:#FFC107,color:#000
```

| Risk | Option A Impact | Option B Impact |
|------|----------------|----------------|
| SAP integration fails | **Medium** (existing POS→SAP but needs SAP modification) | **Medium** (must build new) |
| Data inconsistency | **High** (3 systems) | Low (single system) |
| Staff adoption | Medium (2 UIs) | Medium (new UI) |
| Ongoing cost | **High** (Mendix license) | Low (open source) |
| Vendor lock-in | **High** (Mendix platform) | Low (open source) |
| Scalability | Mendix Cloud (good) | On-prem (maintain) |

---

## 6. Cost Comparison (Estimated)

| Cost Item | Option A (Mendix + POS) | Option B (Odoo CE) |
|-----------|------------------------|-------------------|
| **Development** | | |
| Rental module | Mendix dev: ~xx days | Already built |
| Stock module | Mendix dev: ~xx days | Built-in |
| Mendix ↔ POS integration | ~xx days | N/A |
| SAP integration | ~?? days | ~?? days |
| **Recurring** | | |
| Mendix license | ~?? Baht/user/month | $0 (open source) |
| Hosting | Mendix Cloud (included) | On-prem server (existing) |
| Maintenance | Mendix + POS + SAP | Odoo + SAP |
| **Year 1 estimate** | Higher (dev + license) | Lower (dev only) |
| **Year 2+ estimate** | License continues | Minimal |

---

## 7. Decision Framework

```mermaid
graph TD
    Q1{"Both options need SAP work.<br/>Prefer modifying existing<br/>POS→SAP integration?"}
    Q1 -- "Yes, modify<br/>existing SAP" --> A["Lean toward<br/>Option A"]
    Q1 -- "Prefer building<br/>new clean integration" --> Q2

    Q2{"Budget for<br/>Mendix license?"}
    Q2 -- "Yes" --> Q3
    Q2 -- "Prefer no<br/>recurring cost" --> B["Lean toward<br/>Option B"]

    Q3{"Comfortable with<br/>3-system architecture?"}
    Q3 -- "Yes, IT can<br/>manage it" --> A
    Q3 -- "Prefer simpler<br/>architecture" --> B

    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
```

---

## 8. Recommendation

| Criteria | Winner |
|----------|--------|
| Fastest to production | **Option B** (rental module already built; Option A requires Mendix build from scratch + POS modification) |
| Lowest total cost of ownership | **Option B** (no license fees) |
| Simplest architecture | **Option B** (single system) |
| Best staff experience | **Option B** (single UI) |
| Least integration risk | **Tie** (both require SAP work) |
| Most automation | **Option B** (auto deposit refund) |
| Best data integrity | **Option B** (unified data) |

**Summary:** Option A's perceived advantage of reusing the existing POS → SAP integration is diminished — rental transactions (deposits, refunds, late fees) require significant SAP modification regardless. Additionally, Mendix has no API to POS, forcing staff to manually key in rental document numbers. Option B (Odoo) wins on every criteria: faster to production (rental module already built), lower cost, simpler architecture, better automation, unified data, and both options require comparable SAP integration effort. Option B is the recommended approach.
