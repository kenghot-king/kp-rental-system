# KP Rental System — Enterprise Architecture

> Proposal document for EA review
> Version: 1.0 | Date: 2026-03-23

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        WEB["Odoo Web Client<br/>(Browser)"]
        MOBILE["Mobile / Tablet<br/>(Future)"]
    end

    subgraph "Application Layer — Odoo 19 CE"
        RENTAL["ggg_rental<br/>Rental Management"]
        SALE["sale / sale_stock<br/>Sales & Stock"]
        STOCK["stock<br/>Warehouse & Inventory"]
        ACC["account<br/>Invoicing & Payments"]
        L10N["l10n_th<br/>Thai Localization"]
    end

    subgraph "Integration Layer"
        API["REST API / XML-RPC<br/>Integration Gateway"]
        SCHED["Scheduled Jobs<br/>(ir.cron)"]
        BATCH["Batch Export<br/>Daily FI Documents"]
    end

    subgraph "External Systems"
        SAP["SAP FI<br/>Financial Accounting"]
        SAPSD["SAP SD<br/>Sales & Distribution"]
    end

    subgraph "Data Layer"
        PG["PostgreSQL 16"]
        FS["Filestore<br/>(Attachments)"]
    end

    WEB --> RENTAL
    MOBILE -.-> API
    RENTAL --> SALE
    RENTAL --> STOCK
    SALE --> ACC
    ACC --> L10N
    RENTAL --> API
    API --> BATCH
    BATCH --> SAP
    BATCH --> SAPSD
    SCHED --> BATCH
    RENTAL --> PG
    ACC --> PG
    STOCK --> PG
    PG --> FS
```

### Component Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Odoo 19 CE | Python 3.12 + OWL JS | Core application platform |
| ggg_rental | Odoo module (LGPL-3) | Rental lifecycle management |
| PostgreSQL 16 | Database | Transactional data storage |
| Docker Compose | Containerization | Deployment & environment management |
| SAP FI | ERP (External) | Financial accounting, GL postings |
| SAP SD | ERP (External) | Sales document management |

---

## 2. Rental Workflow

### 2.1 End-to-End Rental Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Quotation: Create Rental Order

    Quotation --> Confirmed: Confirm Order
    note right of Confirmed
        Stock reserved
        Delivery picking created
        (WH/Stock → Rental Location)
    end note

    Confirmed --> PickedUp: Pickup
    note right of PickedUp
        Delivery picking validated
        Serial numbers assigned
        Line notes updated
    end note

    PickedUp --> Returned: Return (Full)
    PickedUp --> PartialReturn: Return (Partial)
    PartialReturn --> Returned: Return (Remaining)

    note right of Returned
        Return move created & validated
        (Rental Location → WH/Stock)
        Stock restored
    end note

    Returned --> Invoiced: Create Invoice
    Invoiced --> Paid: Register Payment

    Confirmed --> Cancelled: Cancel
    PickedUp --> Cancelled: Cancel (Auto-Return)

    note right of Cancelled
        If picked up: auto-return
        moves created for outstanding qty
        If not picked up: picking cancelled
        reservation released
    end note

    Paid --> [*]
    Cancelled --> [*]
```

### 2.2 Pickup Process (Detail)

```mermaid
sequenceDiagram
    actor User
    participant Wizard as Rental Wizard
    participant SOL as Sale Order Line
    participant Move as Stock Move
    participant Quant as Stock Quant

    User->>Wizard: Click "Pickup"
    Wizard->>Wizard: Load available S/N from delivery move
    Wizard->>Wizard: Pre-select reserved S/N
    User->>Wizard: Confirm S/N selection
    Wizard->>SOL: write(qty_delivered, pickedup_lot_ids)

    SOL->>SOL: _validate_rental_pickup()
    SOL->>Move: Find pending delivery move
    SOL->>Move: Assign lot_ids to move lines
    SOL->>Move: Set picked=True
    SOL->>Move: _action_done()
    Move->>Quant: Decrement WH/Stock
    Move->>Quant: Increment Rental Location

    SOL->>SOL: _update_rental_notes()
    Note over SOL: Line name updated:<br/>"Picked up: PB0013"
```

### 2.3 Return Process (Detail)

```mermaid
sequenceDiagram
    actor User
    participant Wizard as Rental Wizard
    participant SOL as Sale Order Line
    participant Move as Stock Move
    participant Quant as Stock Quant

    User->>Wizard: Click "Return"
    Wizard->>Wizard: Show returnable S/N<br/>(picked up - already returned)
    User->>Wizard: Select S/N & qty to return

    alt Late Return
        Wizard->>SOL: _generate_delay_line()
        SOL->>SOL: Calculate late fee<br/>(extra_hourly × hours + extra_daily × days)
        SOL-->>SOL: Create delay charge SO line
    end

    Wizard->>SOL: write(qty_returned, returned_lot_ids)

    SOL->>SOL: _create_rental_return()
    SOL->>Move: Create new move<br/>(Rental Location → WH/Stock)
    SOL->>Move: _action_confirm(merge=False)
    SOL->>Move: _action_assign()
    SOL->>Move: Assign lot_ids, set picked=True
    SOL->>Move: _action_done()
    Move->>Quant: Decrement Rental Location
    Move->>Quant: Increment WH/Stock

    SOL->>SOL: _update_rental_notes()
    Note over SOL: Line name updated:<br/>"Picked up: PB0013<br/>Returned: PB0013"
```

### 2.4 Stock Flow Visualization

```mermaid
graph LR
    subgraph "Warehouse"
        WH["WH/Stock<br/>On Hand: 10<br/>Free to Use: 8"]
    end

    subgraph "Rental Zone"
        RL["Rental Location<br/>(Internal)"]
    end

    WH -- "① Confirm SO<br/>Reserve qty=2<br/>(Free to Use: 8→6)" --> WH
    WH -- "② Pickup<br/>Validate delivery picking" --> RL
    RL -- "③ Return<br/>New return move" --> WH

    style WH fill:#4CAF50,color:#fff
    style RL fill:#FF9800,color:#fff
```

### 2.5 Serial Number Lifecycle

```mermaid
graph TD
    A["S/N: PB0013<br/>📍 WH/Stock<br/>Status: Available"] -- "SO Confirmed" --> B["S/N: PB0013<br/>📍 WH/Stock<br/>Status: Reserved"]
    B -- "Pickup" --> C["S/N: PB0013<br/>📍 Rental Location<br/>Status: Rented"]
    C -- "Return" --> D["S/N: PB0013<br/>📍 WH/Stock<br/>Status: Available"]

    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#4CAF50,color:#fff
```

---

## 3. SAP Integration

### 3.1 Integration Overview

```mermaid
graph LR
    subgraph "Odoo 19 CE"
        INV["Invoices<br/>(account.move)"]
        PAY["Payments<br/>(account.payment)"]
        CRON["Daily Cron Job<br/>(Scheduled)"]
    end

    subgraph "Integration Layer"
        EXPORT["Batch Export<br/>Service"]
        MAP["Field Mapping<br/>& Transformation"]
        LOG["Integration Log<br/>& Error Handling"]
    end

    subgraph "SAP"
        FI["SAP FI<br/>FI Document"]
        GL["General Ledger"]
        AR["Accounts Receivable"]
        SD["SAP SD<br/>Sales Document"]
    end

    CRON --> EXPORT
    INV --> EXPORT
    PAY --> EXPORT
    EXPORT --> MAP
    MAP --> FI
    MAP --> SD
    FI --> GL
    FI --> AR
    EXPORT --> LOG
```

### 3.2 Daily Integration Flow

```mermaid
sequenceDiagram
    participant Cron as Odoo Cron<br/>(Daily 00:00)
    participant Odoo as Odoo DB
    participant Export as Export Service
    participant SAP as SAP FI/SD

    Note over Cron,SAP: Daily Batch — End of Day

    Cron->>Odoo: Query posted invoices<br/>(state=posted, not yet synced)
    Odoo-->>Cron: Invoice records

    Cron->>Export: Prepare FI documents

    loop Each Invoice
        Export->>Export: Map Odoo → SAP fields
        Note over Export: Document Type: DR (Debit)<br/>Company Code: from Odoo company<br/>GL Account: from account mapping<br/>Tax Code: from tax mapping
    end

    Export->>SAP: POST FI Documents (Batch)
    SAP-->>Export: SAP Document Numbers

    Export->>Odoo: Update sync status<br/>(sap_doc_number, synced=True)

    Cron->>Odoo: Query registered payments<br/>(not yet synced)
    Odoo-->>Cron: Payment records

    Cron->>Export: Prepare clearing documents

    Export->>SAP: POST Clearing Documents
    SAP-->>Export: Clearing Doc Numbers
    Export->>Odoo: Update payment sync status
```

### 3.3 Field Mapping — Odoo Invoice → SAP FI Document

| Odoo Field | SAP FI Field | Description |
|-----------|-------------|-------------|
| `account.move.name` | `BELNR` (Reference) | Invoice number (INV/2026/00001) |
| `account.move.invoice_date` | `BUDAT` (Posting Date) | Invoice posting date |
| `account.move.invoice_date` | `BLDAT` (Document Date) | Document date |
| `res.company.name` | `BUKRS` (Company Code) | Company code mapping |
| `account.move.partner_id` | `KUNNR` (Customer) | Customer master mapping |
| `account.move.currency_id` | `WAERS` (Currency) | Currency code (THB) |
| `account.move.amount_untaxed` | `WRBTR` (Amount) | Net amount |
| `account.move.amount_tax` | Tax line amount | VAT amount |
| `account.move.amount_total` | Total | Gross amount |
| Invoice line account | `HKONT` (GL Account) | Revenue GL account |
| Tax code (VAT 7%) | `MWSKZ` (Tax Code) | Output tax code |

### 3.4 SAP Document Types

| Scenario | SAP Doc Type | Source in Odoo |
|----------|-------------|----------------|
| Rental Invoice | `DR` (Customer Invoice) | `account.move` (type=out_invoice) |
| Credit Note | `DG` (Credit Memo) | `account.move` (type=out_refund) |
| Payment Receipt | `DZ` (Payment) | `account.payment` |
| Late Fee Invoice | `DR` (Customer Invoice) | Delay charge line in invoice |

### 3.5 Integration Error Handling

```mermaid
graph TD
    A[Export Batch] --> B{SAP Response}
    B -- "Success" --> C[Update Odoo:<br/>synced=True<br/>sap_doc_number]
    B -- "Partial Failure" --> D[Log failed records]
    D --> E[Retry on next run]
    B -- "Connection Error" --> F[Alert & retry<br/>next scheduled run]

    C --> G[Generate<br/>reconciliation report]
    E --> G

    style C fill:#4CAF50,color:#fff
    style D fill:#FF9800,color:#fff
    style F fill:#f44336,color:#fff
```

---

## 4. Data Flow Summary

```mermaid
graph TB
    subgraph "Odoo — Operational"
        SO["Sale Order<br/>(Rental)"] --> INV["Invoice"]
        SO --> PICK["Stock Picking<br/>(Delivery/Return)"]
        INV --> PAY["Payment"]
    end

    subgraph "Odoo — Accounting"
        INV --> JE["Journal Entry"]
        PAY --> JE2["Payment Entry"]
        JE --> GL_O["Odoo GL"]
        JE2 --> GL_O
    end

    subgraph "SAP — Financial"
        GL_O -- "Daily Batch" --> FI_DOC["FI Document"]
        FI_DOC --> GL_S["SAP GL"]
        FI_DOC --> AR_S["SAP AR"]
        PAY -- "Daily Batch" --> CLR["Clearing Doc"]
        CLR --> AR_S
    end

    style SO fill:#2196F3,color:#fff
    style INV fill:#4CAF50,color:#fff
    style FI_DOC fill:#FF9800,color:#fff
```

---

## 5. Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose"
        subgraph "Application"
            CE["odoo-ce<br/>Port: 8069<br/>Odoo 19 CE"]
            EE["odoo-ee<br/>Port: 8070<br/>Odoo 19 EE<br/>(profile: ee)"]
        end

        subgraph "Database"
            PG["PostgreSQL 16<br/>pgdata volume"]
        end

        CE --> PG
        EE -.-> PG
    end

    subgraph "Volumes"
        ADDONS["./addons<br/>Custom modules"]
        ENT["./enterprise<br/>EE modules (ro)"]
    end

    ADDONS --> CE
    ADDONS --> EE
    ENT --> EE

    subgraph "Custom Modules"
        GR["ggg_rental<br/>Rental Management"]
        GG["ggg_gantt<br/>Gantt View"]
    end

    GR --> ADDONS
    GG --> ADDONS
```

---

## 6. Key Decisions & Considerations

### SAP Integration Approach

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Real-time API** | Immediate sync | Complex error handling, SAP availability dependency | Not recommended |
| **Daily batch** | Simple, reliable, auditable | Data delay (T+1) | **Recommended** |
| **Near real-time (queue)** | Low latency, decoupled | Infrastructure complexity (message broker) | Future phase |

### Integration Technology Options

| Option | Description | Fit |
|--------|------------|-----|
| **Odoo Cron + Python** | Scheduled job exports CSV/JSON, calls SAP RFC/BAPI | Simple, no extra infra |
| **Middleware (MuleSoft, etc.)** | Enterprise integration platform | Overkill for this scope |
| **SAP PI/PO** | SAP's own integration platform | If SAP team mandates it |
| **File-based (SFTP)** | Odoo exports flat file, SAP imports via batch input | Low-tech, proven pattern |

### Recommended: Odoo Cron + File Export

```
Odoo (Daily Cron)
  → Generate CSV/iDoc flat file
  → Upload to SFTP / shared folder
  → SAP Batch Input picks up file
  → Posts FI documents
  → Returns status file
  → Odoo reads status & updates sync flag
```

---

## 7. Open Items

- [ ] SAP company code mapping to Odoo company
- [ ] SAP customer master sync (manual or automated?)
- [ ] GL account mapping table between Odoo CoA and SAP CoA
- [ ] SAP tax code mapping for Thai VAT 7%
- [ ] File format specification (CSV, iDoc, BAPI?)
- [ ] SFTP / connectivity details
- [ ] Error notification channel (email, LINE, etc.)
- [ ] Reconciliation report requirements
- [ ] Go-live cutover plan (parallel run period?)
