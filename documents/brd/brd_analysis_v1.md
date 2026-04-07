# BRD Analysis v1.1 — RTB Requirement List v1.1

> Source: `RTB requirement list v.1.1.xlsx` Sheet1
> Last updated: 2026-04-06
> Cross-referenced against: `addons/ggg_rental/` codebase

---

## Legend

| Symbol | Meaning |
|--------|---------|
| DONE | Already implemented in current codebase |
| PARTIAL | Foundation exists, needs additional work |
| NEW | No implementation exists, needs development |
| DEFERRED | Next Phase / TBC — not in Phase 1 scope |
| N/A | Handled outside Odoo or not applicable |

| Effort | Meaning |
|--------|---------|
| S | Small — config or minor field addition (< 1 day) |
| M | Medium — new view, wizard, or report (1–3 days) |
| L | Large — new module, integration, or complex logic (3–7 days) |
| XL | Extra Large — external system integration or major feature (1–3 weeks) |

---

## 1. Product Master (#1–#7)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 1 | Create product master ตาม Odoo standard | 1 | DONE | — | `product.template` with `rent_ok`, pricing rules, `is_rental_deposit` flag |
| 2 | Custom fields เพิ่มจาก standard | Next | DEFERRED | S–M | Depends on what fields are needed |
| 3 | Maintain article master (key-in & upload) | 1 | DONE | — | Standard Odoo UI + CSV/XLSX import built-in |
| 4 | Step price ตาม standard (daily, 3-day, weekly, 2-week) | 1 | DONE | — | `product.pricing` + `sale.temporal.recurrence` supports hourly, daily, 3-day, weekly, 2-week, monthly, overnight |
| 5 | Step price นอกเหนือ standard | Next | DEFERRED | S | Just add more `sale.temporal.recurrence` records |
| 6 | Auto sync product master จาก SAP | Next | DEFERRED | XL | SAP API integration needed |
| 7 | Tax setup per product | 1 | DONE | — | Standard Odoo tax + fiscal position system; `l10n_th` Thai localization installed |

**Blocked on business input:**
- **#1**: Confirm ว่า standard Odoo fields เพียงพอหรือไม่?
- **#4**: Confirm ราคาเช่าแต่ละ step ในแต่ละ article
- **#7**: ราคาเป็นราคารวมภาษีหรือยัง? VAT rate?

---

## 2. Inventory Management (#8–#10)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 8 | Serial number tracking | 1 | DONE | — | Full lot tracking: `pickedup_lot_ids`/`returned_lot_ids` on SOL, `damage_log_ids` on `stock.lot` |
| 9 | Lock serial number จากการเช่า | TBC | PARTIAL | M | Stock moves provide implicit locking. Need explicit `rental_status` field on `stock.lot` (available/damaged/inspection) + domain filter in wizard |
| 10 | Inventory แยกสาขา | Next | DEFERRED | L | Odoo multi-warehouse exists. Needs branch config + inter-branch transfer workflow |

**Blocked on business input:**
- **#9**: สถานะที่ห้ามปล่อยเช่ามีอะไรบ้าง? (ชำรุด/กำลังตรวจสภาพ/สงวนไว้/อื่นๆ?) ใครมี lock/unlock?
- **#10**: มีสาขาอะไรบ้าง? โอนข้ามสาขา?

---

## 3. Customer Master (#11–#14)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 11 | Create customer profile ตาม Odoo standard | 1 | DONE | — | `res.partner` with Thai localization |
| 12 | Custom fields for customer | Next | DEFERRED | S–M | Depends on fields needed |
| 13 | Connect customer DB จาก GWL | Next | DEFERRED | XL | GWL API spec unknown |
| 14 | Multiple contacts under 1 customer | 1 | DONE | — | Odoo standard parent/child contacts, `partner_invoice_id`, `partner_shipping_id` |

**Blocked on business input:**
- **#11**: Customer master fields ที่ต้องการเพิ่มเติมจาก standard?

---

## 4. Rental Process (#15–#17)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 15 | Check stock availability ก่อน create customer | 1 | DONE | — | Product availability in list/form + Gantt schedule view (`ggg_gantt`) |
| 16 | Generate quotation PDF | 1 | PARTIAL | M | QWeb report exists (`report_rental_order`) but titled "Pickup and Return Receipt". Need separate quotation layout |
| 17 | Confirm quotation & reserve serial numbers | 1 | DONE | — | SO confirm → delivery move created (reserved). Serial assignment at pickup via wizard |

**Blocked on business input:**
- **#16**: ขอตัวอย่าง/layout ใบ Quotation

---

## 5. Rental Process — Payment (#18–#30)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 18 | Payment: credit card, QR, 2c2p, EDC | 1 | PARTIAL | M | Payment journals configured (VISA, MASTER, QR PromptPay, CASH, Transfer). No 2c2p/EDC system integration. Phase 1 = manual |
| 19 | Manual key rental ref on 2c2p link | 1 | NEW | S | Text field `payment_ref_2c2p` on SO or invoice |
| 20 | Store 2c2p ref in rental payment field | 1 | NEW | S | Same as #19 |
| 21 | Manual key rental ref on EDC | 1 | NEW | S | Text field `edc_payment_ref` on SO |
| 22 | Store EDC deposit ref (hold) | 1 | NEW | S | Text field `edc_deposit_ref` on SO |
| 23 | Generate: ABB, Receipt/Tax Invoice (original+copy), สัญญาเช่า (original+copy), ใบตรวจรับ | 1 | PARTIAL | L | Only "Pickup and Return Receipt" PDF exists. Need 4+ new QWeb templates with original/copy variants |
| 24 | Pre-fill customer data in documents | Next | DONE | — | QWeb templates already pull from `res.partner` |
| 25 | ABB registration number | 1 | NEW | S | Config field for ABB registration + template |
| 26 | Select contact for tax invoice | TBC | DONE | — | Standard Odoo `partner_invoice_id` on SO |
| 27 | Upload related documents | 1 | DONE | — | Standard Odoo `ir.attachment` / chatter |
| 28 | Digital signature on documents | TBC | PARTIAL | M | Odoo EE `sign` module. CE alternative needed (e.g. portal signature widget) |
| 29 | Void — return same day as payment | Next | DEFERRED | M | Credit note + void logic |
| 30 | Refund — return different day | Next | PARTIAL | — | Deposit credit note auto-creation already exists |

**Blocked on business input:**
- **#18–#22**: BU confirmation — payment method แต่ละรายการถูกต้อง? Phase 1 = manual ทั้งหมดใช่?
- **#23**: ขอตัวอย่างเอกสารทุกชนิด (ABB, Receipt, Tax Invoice, สัญญาเช่า, ใบตรวจรับ) — ต้องออกกี่ชุด? ต้นฉบับ/สำเนาแยกอย่างไร?
- **#25**: ขอเลขทะเบียน ABB จากบัญชี
- **#28**: Digital signature แบบไหน? (draw on screen? OTP? certificate?)

---

## 6. Rental Return Process — Payment (#31–#39)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 31 | Manual key-in ค่าปรับ (penalty) | TBC→P1 | DONE | — | Auto-calculated delay fee: `(hourly_rate × hours) + (daily_rate × days)` with configurable grace period (`min_extra_hour`) |
| 32 | Manual key-in ค่าเสียหาย/สูญหาย | TBC→P1 | DONE | — | `damage_fee` field in return wizard → `_generate_damage_line()` creates SO line. `rental.damage.log` per serial |
| 33 | Manual key-in net refund (deposit − penalty − damage) | TBC→P1 | DONE | — | `_create_deposit_credit_note()` creates proportional credit note. Auto-refund payment via `deposit_auto_refund` |
| 34 | Penalty fee as formula/step | Next | PARTIAL | M | Current: daily+hourly. Step-based pricing TBD |
| 35 | Damage fee as formula/step | Next | DEFERRED | M | Currently flat manual entry. Formula/step needs spec |
| 36 | EDC refund at store (manual, no system link) | TBC→P1 | N/A | S | Process outside Odoo. May need field to store EDC refund ref |
| 37 | Generate ใบรับคืนสินค้า (return receipt) | TBC→P1 | PARTIAL | M | Current PDF is combined "Pickup and Return Receipt". Separate return-only document recommended |
| 38 | Generate ใบเสร็จ for penalties/damage | TBC→P1 | NEW | M | New QWeb report template needed |
| 39 | Upload return documents | 1 | DONE | — | Standard Odoo attachments / chatter |

**Blocked on business input:**
- **#36**: Process เหมือนปัจจุบัน? ต้องเก็บ EDC refund ref? ต้องมี approval flow?
- **#37**: ใบรับคืนแยกจากใบตรวจรับ? (แนะนำ: แยก)
- **#38**: ขอ layout ใบเสร็จค่าปรับ/ค่าเสียหาย

---

## 7. Accounting Posting (#40–#42)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 40 | Generate file for SAP upload | 1 | NEW | L | EA doc proposes daily batch export (invoice → SAP FI document). No code yet |
| 41 | Auto-connect to SAP | Next | DEFERRED | XL | Full SAP API integration |
| 42 | Post under company KPC | 1 | PARTIAL | S | Multi-company exists. Needs SAP GL mapping + cost center config |

**Blocked on business input:**
- **#40**: SAP file format spec (CSV/XML?), field mapping (GL account, cost center, tax code), frequency (daily/weekly?), delivery (SFTP/shared folder?), who uploads?
- **#42**: รหัสบริษัท KPC, GL account mapping

---

## 8. Sales Process (#43–#47)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 43 | Buy without prior rental | TBC | DONE | — | `sale_ok=True` products can be sold via regular SO. Mixed SO lines (rental + sale) supported |
| 44 | Sales process support | TBC | PARTIAL | M | Standard Odoo SO flow works. May need POS-like flow for walk-in |
| 45 | Depreciation calculation for sale price | TBC | NEW | L | Need depreciation formula/table per product. No standard Odoo support |
| 46 | EDC ref for sales | TBC | NEW | S | Same pattern as #21 |
| 47 | Generate sales documents | TBC | PARTIAL | M | Standard Odoo invoice PDF exists. May need template for second-hand condition disclosure |

**Blocked on business input:**
- **#43–#44**: Process การขายหน้าร้าน? ขายผ่าน LINE ได้? คืนสินค้าได้หรือไม่? (วัน/ข้ามวัน/ภายในกี่วัน?)
- **#45**: ค่าเสื่อมเอามาจากไหน? สูตรคำนวณ? ใส่ที่ master?
- **#47**: เอกสารที่ต้องออก? บอกสภาพ/ตำหนิ?

---

## 9. Reporting (#48)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 48 | Standard Odoo rental reports | 1 | DONE | — | `sale.rental.report` SQL view: daily aggregation, pivot/graph/list. Dimensions: date, product, customer, salesman |

**Blocked on business input:**
- **#48**: Report เพิ่มเติม? (revenue, utilization, overdue, damage stats?) ความถี่? Export format?

---

## 10. System Integrations (#49–#53)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 49 | LINE OA integration | Next | DEFERRED | XL | LINE Messaging API + webhook |
| 50 | EDC/2c2p auto integration | Next | DEFERRED | XL | Payment gateway API |
| 51 | SAP auto integration | Next | DEFERRED | XL | SAP RFC/BAPI or REST |
| 52 | GWL auto integration | Next | DEFERRED | XL | GWL API spec unknown |
| 53 | OneTrust auto integration | Next | DEFERRED | XL | Privacy/consent management |

> All integrations are "Next Phase". No action needed now.

---

## 11. RBAC (#54)

| # | Requirement | Phase | Status | Effort | Notes |
|---|-------------|-------|--------|--------|-------|
| 54 | Role-based access per BU/level | Next | PARTIAL | L | Current: basic Salesman/Manager groups. Need BU-specific groups (e.g. finance read-only on accounting data) + record rules |

---

## Summary Dashboard

### Overall Status (54 requirements)

```
DONE          ████████████████░░░░░░░░░░░░  17  (31%)
PARTIAL       ████████░░░░░░░░░░░░░░░░░░░░   9  (17%)
NEW           ██████████░░░░░░░░░░░░░░░░░░  10  (19%)
DEFERRED      ██████████████░░░░░░░░░░░░░░  17  (31%)
N/A           █░░░░░░░░░░░░░░░░░░░░░░░░░░░   1  ( 2%)
```

### Phase 1 + TBC→P1 Items (30 items)

```
DONE          ████████████████████░░░░░░░░  14  (47%)
PARTIAL       ██████████░░░░░░░░░░░░░░░░░░   6  (20%)
NEW           ████████░░░░░░░░░░░░░░░░░░░░   8  (27%)
N/A           █░░░░░░░░░░░░░░░░░░░░░░░░░░░   1  ( 3%)
DEFERRED/TBC  █░░░░░░░░░░░░░░░░░░░░░░░░░░░   1  ( 3%)
```

### Phase 1 Remaining Work by Effort

| Effort | Count | Items |
|--------|-------|-------|
| S | 6 | #19, #20, #21, #22, #25, #36 |
| M | 5 | #9, #16, #28, #37, #38 |
| L | 2 | #23 (doc templates), #40 (SAP export) |
| **Total** | **13** | est. **3–4 weeks** of development |

---

## Top Blockers

```
┌─ PRIORITY 1 — Unblock first ─────────────────────────────────────┐
│                                                                   │
│  1. Document templates (samples/layouts)         → blocks 6 items │
│     #16 Quotation, #23 ABB/Receipt/Contract/     (most impact)    │
│     Inspection, #37 Return receipt, #38 Fee receipt               │
│                                                                   │
│  2. Payment process BU confirmation              → blocks 5 items │
│     #18–#22 confirm method per transaction type  (quick to get)   │
│                                                                   │
│  3. SAP file format spec                         → blocks 2 items │
│     #40 file export, #42 KPC config              (long lead time) │
│                                                                   │
├─ PRIORITY 2 — Can wait ──────────────────────────────────────────┤
│                                                                   │
│  4. Serial lock statuses (#9)                                     │
│  5. Report requirements (#48)                                     │
│  6. Return/refund EDC process detail (#36)                        │
│  7. ABB registration number from accounting (#25)                 │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Appendix: Questions for Business Team

### A. Document Templates (CRITICAL — blocks most Phase 1 items)
1. ขอตัวอย่างเอกสารที่ใช้อยู่ปัจจุบัน (กระดาษ/Excel/PDF):
   - ใบ Quotation
   - ABB (Abbreviated Tax Invoice)
   - ใบเสร็จรับเงิน / ใบกำกับภาษี (Receipt / Tax Invoice)
   - สัญญาเช่า (Rental Contract)
   - ใบตรวจรับสินค้า (Pickup Inspection)
   - ใบรับคืนสินค้า (Return Receipt)
   - ใบเสร็จค่าปรับ/ค่าเสียหาย (Penalty/Damage Receipt)
2. แต่ละเอกสารต้องออกกี่ชุด? แยกต้นฉบับ/สำเนาหรือไม่?
3. ต้องออก Invoice ให้ลูกค้าหรือไม่? ออกตอนไหน?

### B. Payment Methods (blocks 5 items)
4. ค่าเช่าจ่ายผ่าน 2c2p (LINE) — ยืนยันใช่หรือไม่?
5. ค่ามัดจำ hold ผ่าน EDC — ยืนยันใช่หรือไม่?
6. ค่าปรับ/ค่าเสียหาย จ่ายผ่าน EDC — ยืนยันใช่หรือไม่?
7. Phase 1 เป็น manual key ref ทั้งหมดใช่หรือไม่? (ไม่เชื่อมต่อ 2c2p/EDC)

### C. SAP Integration (blocks 2 items, long lead time)
8. File format ที่ SAP ต้องการ (CSV, XML, fixed-width)?
9. Field mapping: ข้อมูลอะไรบ้าง (GL account, cost center, tax code)?
10. ความถี่การ gen file (daily, weekly)?
11. วาง file ไว้ที่ไหน (SFTP, shared folder)?
12. ใครเป็นคน upload เข้า SAP?
13. รหัสบริษัท KPC + GL mapping

### D. Serial Number Management
14. สถานะที่ห้ามปล่อยเช่ามีอะไรบ้าง? (ชำรุด/ตรวจสภาพ/สงวน/อื่นๆ)
15. ใครมีสิทธิ์ lock/unlock?

### E. Reports
16. ต้องการ report อะไรบ้างนอกเหนือจาก Rental Analysis?
17. ความถี่ (daily, weekly, monthly)?
18. Export format (PDF, Excel)?

### F. Return Process
19. EDC refund ที่หน้าร้าน — process เหมือนปัจจุบัน?
20. ต้องเก็บ EDC refund ref ในระบบ?
21. ต้องมี approval flow ก่อน refund?
