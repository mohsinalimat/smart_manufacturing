# Module Definitions & Functional Flows

---

## 1. Production Planning

### Definition
Manages the scheduling of manufacturing work against available capacity, providing
finite-capacity planning, shift scheduling, bottleneck detection, and production
forecasting for multi-workstation environments.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `Production Schedule` | Master schedule linking work orders to dates, shifts, and workstations |
| `Capacity Plan` | Per-workstation capacity analysis (planned vs available hours) |
| `Shift Plan` | Assigns operators to workstations per shift per date |
| `Production Forecast` | Item-level demand forecasting with actual vs forecast variance |
| `Workstation Schedule` | Daily availability calendar for each workstation |
| `SM Bottleneck Log` | Records detected capacity overloads with severity and resolution |

### Functional Flow
```
1. Planner creates Production Schedule
       │
       ├── Links Work Orders to workstations and dates
       ├── Sets schedule_type (Finite/Infinite/Machine-wise/Shift-wise)
       └── Submits for approval

2. On submission → background job recalculates:
       │
       ├── total_machine_hours (sum across all work orders)
       ├── total_labor_hours
       └── bottleneck_detected (if any workstation > capacity × days)

3. If bottleneck detected:
       └── SM Bottleneck Log created + real-time alert published

4. Approved schedule → Work Orders get sm_production_schedule linked
       └── SM Cost Sheet auto-created per Work Order
```

### ERPNext Integration Points
- `Work Order` — custom fields: `sm_production_schedule`, `sm_shift`, `sm_cost_sheet`, `sm_oee`
- `Workstation` — custom fields: `sm_machine_cost_per_hour`, `sm_planned_capacity_hours`, `sm_equipment`
- Hook: `Work Order.on_submit` → links schedule, creates cost sheet

---

## 2. Shop Floor Execution

### Definition
Provides real-time production tracking at the operator level — job card management,
barcode/QR scanning, downtime recording, scrap logging, operator assignment,
and shift performance tracking — via a tablet/mobile-optimized terminal UI.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Downtime Log` | Records machine/workstation downtime with type, cause, and duration |
| `SM Scrap Rejection Log` | Captures scrap/rejection events with defect codes and values |
| `SM Operator Assignment` | Assigns operators to workstations and work orders per shift |
| `SM Shift Log` | Summarizes shift performance: planned vs actual qty, OEE, downtime |

### Key Page
**Shop Floor Terminal** (`/shop_floor-terminal`) — A full browser-based shop floor
terminal with:
- Live job card grid (filtered by workstation)
- One-click Start / Complete job card
- Barcode and QR code scanning (resolves to Work Order, Job Card, or Item)
- Inline downtime logging dialog
- Inline scrap/rejection logging dialog
- Live OEE badge per workstation
- Mobile-responsive layout

### Functional Flow
```
Operator opens Shop Floor Terminal
       │
       ├── Selects workstation (or scans workstation QR)
       │
       ├── Views active Job Cards → status: Open | Work In Progress
       │
       ├── START button:
       │     ├── Job Card Time Log entry created (from_time = now)
       │     ├── sm_operator set to current user
       │     └── Job Card status → Work In Progress
       │
       ├── COMPLETE button:
       │     ├── Dialog: enter qty_completed, scrap_qty
       │     ├── Job Card Time Log closed (to_time = now)
       │     ├── SM Shift Log updated (actual_qty += qty_completed)
       │     └── If Work Order has QC template → Quality Inspection auto-created
       │
       ├── LOG SCRAP button:
       │     └── SM Scrap Rejection Log created
       │
       └── LOG DOWNTIME button:
             ├── SM Downtime Log created (from_time = now)
             └── End Downtime → downtime_minutes computed, log submitted
```

### ERPNext Integration Points
- `Job Card` — custom fields: `sm_operator`, `sm_downtime_minutes`, `sm_scrap_qty`, `sm_qc_status`
- Hook: `Job Card.on_submit` → updates downtime totals, triggers QC creation, updates shift log
- REST API: `api/shop_floor.py` — IoT/tablet endpoints for `record_production`, `start_downtime`, `end_downtime`, `scan_barcode`

---

## 3. Manufacturing Costing

### Definition
Captures the full cost of production at the work order level — breaking down
material, labor, machine, and overhead costs — and computes variance against
standard (planned) costs to enable cost control and profitability analysis.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Cost Sheet` | Per-work-order cost summary (standard vs actual, variance analysis) |
| `SM Machine Cost Rate` | Machine cost breakdown (depreciation + power + maintenance + consumables) per workstation |
| `SM Overhead Template` | Overhead allocation rules (fixed, per hour, % of material) |
| `SM Labor Cost Rate` | Labor cost rates per designation (basic + overtime + benefits) |
| `SM Cost Variance Log` | Historical variance records per cost sheet period |

### Cost Components
```
Total Production Cost = Material Cost
                      + Labor Cost
                      + Machine Cost
                      + Overhead Cost
                      + Utility Cost (optional)
```

### Functional Flow
```
Work Order submitted
       │
       └── SM Cost Sheet auto-created (status: Open)
               │
               ├── std_material_cost   ← from BOM item costs
               ├── std_labor_cost      ← from SM Labor Cost Rate × planned hours
               ├── std_machine_cost    ← from SM Machine Cost Rate × planned hours
               └── std_overhead_cost   ← from SM Overhead Template

Hourly background job (update_wip_costs):
       │
       └── For each open SM Cost Sheet:
               ├── act_material_cost  ← Stock Entry amounts (Material Transfer for Manufacture)
               ├── act_labor_cost     ← Job Card time logs × employee CTC rate
               ├── act_machine_cost   ← Job Card time logs × SM Machine Cost Rate
               └── act_overhead_cost  ← 15–20% of machine cost (or template-based)

Cost Sheet closed monthly:
       └── Variance = Actual - Standard
           Variance % computed
           Status → Closed
```

### ERPNext Integration Points
- `Work Order.on_submit` → creates `SM Cost Sheet`
- `Stock Entry.on_submit` → updates `act_material_cost`
- `Job Card.on_submit` → updates `act_labor_cost`, `act_machine_cost`

---

## 4. SM Quality Management

### Definition
Provides stage-wise quality inspection workflows, non-conformance management,
corrective and preventive action (CAPA) tracking, and quality alerting — aligned
with ISO 9001 requirements and suitable for pharmaceutical, food, automotive,
and textile industries.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Inline QC` | Stage-specific quality inspection (Incoming / In-Process / Final / Outgoing) |
| `SM Inspection Template` | Reusable inspection parameter sets with AQL sampling plans |
| `SM CAPA` | Corrective and Preventive Action with root cause analysis and action tracking |
| `SM NCR` | Non-Conformance Report with disposition (Use As Is / Rework / Scrap / Quarantine) |
| `SM Quality Alert` | Real-time quality alerts with severity levels and acknowledgement workflow |

### Functional Flow
```
Quality Inspection triggered (auto from Job Card, or manual):
       │
       ├── Inspector uses SM Inline QC
       │     ├── Selects SM Inspection Template (loads parameters)
       │     ├── Records actual values per parameter (vs min/max)
       │     └── Sets Overall Status: Passed / Failed / Conditional Pass
       │
       ├── If PASSED:
       │     └── sm_qc_status on Job Card → "Passed"
       │
       └── If FAILED:
             ├── SM NCR auto-created (item, work order, NC type)
             ├── SM Quality Alert created (severity: High, real-time push)
             └── CAPA linked to NCR

SM NCR → disposition decision:
       ├── Use As Is      → proceed
       ├── Rework         → re-queue to workstation
       ├── Scrap          → SM Scrap Rejection Log created
       └── Quarantine     → hold location assigned

SM CAPA lifecycle:
       Open → Under Review → Root Cause Analysis
       → Action Plan (SM CAPA Action items assigned)
       → Verification → Effectiveness check → Closed
```

### ERPNext Integration Points
- `Quality Inspection.on_submit` → creates SM NCR + SM Quality Alert on rejection
- `Job Card.on_submit` → auto-creates Quality Inspection if QC template on Work Order
- `BOM` — custom fields: `sm_revision`, `sm_ecr_reference`

---

## 5. MRP Enhanced

### Definition
Extends ERPNext's Material Requirements Planning with demand forecasting,
real-time shortage prediction, dynamic safety stock calculation, and
auto-generated procurement recommendations — reducing stockouts and
excess inventory simultaneously.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Demand Forecast` | Item-level demand forecasts (Moving Average, Exponential Smoothing, Sales-based) |
| `SM Material Shortage Alert` | Auto-generated alerts when stock < required qty for open work orders |
| `SM Procurement Recommendation` | Consolidated purchase recommendations grouped by severity |
| `SM Safety Stock Policy` | Per-item safety stock rules (Fixed / Days of Supply / Service Level / Statistical) |

### Functional Flow
```
Daily MRP Run (background job):
       │
       ├── For each open Work Order:
       │     ├── Explode BOM → required qty per item
       │     ├── Check current stock (tabBin)
       │     └── If stock < required → SM Material Shortage Alert
       │
       ├── Shortage alerts:
       │     ├── Severity: Critical (>50% short) / High (>20%) / Medium
       │     └── Real-time push notification to planners
       │
       └── SM Procurement Recommendation generated weekly:
             └── Groups alerts by item → links preferred supplier → Required By date

Dynamic Reorder Point (weekly):
       │
       ├── avg_daily_demand = sales last 90 days / 90
       ├── safety_stock:
       │     ├── Fixed: from policy
       │     ├── Days of Supply: avg_demand × days_of_supply
       │     └── Statistical: avg_demand × lead_time × 0.25
       └── reorder_point = avg_daily_demand × lead_time + safety_stock
             └── Written to Item.sm_reorder_point
```

### ERPNext Integration Points
- `Purchase Order.on_submit` → updates related SM Material Shortage Alerts to "PO Raised"
- `Item` — custom fields: `sm_safety_stock`, `sm_reorder_point`, `sm_industry_type`

---

## 6. Batch & Traceability

### Definition
Provides complete forward and backward traceability for manufactured batches —
automatically building genealogy trees from stock entries, enabling product recalls,
and monitoring batch expiry — critical for food, pharma, and chemical industries.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Batch Genealogy` | Complete family tree of a batch (parent ingredients + child outputs + all movements) |
| `SM Recall Order` | Formal recall document with affected batch list and retrieval tracking |
| `SM Lot Tracking Log` | Chronological event log for any lot (manufactured, transferred, sold, returned, recalled) |

### Functional Flow
```
Stock Entry (Manufacture) submitted:
       │
       └── SM Batch Genealogy auto-built:
               ├── batch_no        = finished goods batch
               ├── parent_batches  = all raw material batches consumed
               │     (from Stock Entry Detail where batch_no is set)
               └── stock_movements = [{ voucher: SE name, qty, warehouse }]

Forward Trace (What was made FROM this batch?):
       └── SM Batch Genealogy.child_batches → delivery notes, invoices

Backward Trace (What went INTO this batch?):
       └── SM Batch Genealogy.parent_batches → supplier batches, GRN refs

Product Recall:
       ├── SM Recall Order created (Class I / II / III)
       ├── Affected batches listed with current location
       ├── Status tracked: Not Located → Located → Retrieved → Destroyed
       └── Regulatory body notification date recorded

Expiry Alerts (daily job):
       └── Batches expiring within 30 days → real-time alert pushed
```

### API
`GET /api/method/smart_manufacturing.api.quality.get_batch_trace`
Returns full genealogy: `{ genealogy, ingredients, outputs }` for any batch number.

---

## 7. Subcontract Manufacturing

### Definition
Manages the full lifecycle of third-party manufacturing operations — from raw
material issuance to supplier work tracking, finished goods receipt, material
reconciliation, and subcontract costing.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Supplier Work Order` | Tracks production at supplier site (material issued, qty received, status) |
| `SM Subcontract Cost Sheet` | Breaks down subcontract costs (raw material + processing + freight + other) |

### Functional Flow
```
Subcontracting Order (ERPNext) submitted:
       │
       └── SM Supplier Work Order auto-created per line item
               ├── supplier, item, qty, planned dates
               └── status → Draft

Material issuance:
       ├── Stock Entry (Send to Subcontractor) created in ERPNext
       └── SM Supplier Work Order materials tab updated

Production at supplier:
       └── Status updates: Draft → Material Issued → In Production → Completed

Finished goods receipt:
       ├── Subcontracting Receipt (ERPNext) created
       ├── received_qty updated on SM Supplier Work Order
       └── Reconciliation: issued - received = outstanding

SM Subcontract Cost Sheet:
       └── Captures: raw_material_cost + processing_cost + freight_cost
               └── cost_per_unit computed for profitability analysis
```

---

## 8. Maintenance & Equipment

### Definition
Tracks manufacturing equipment across its full lifecycle — planned preventive
maintenance, condition-based scheduling, breakdown management, spare parts
inventory, and utilization reporting — to maximize equipment uptime and OEE.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Equipment` | Equipment master with technical specs, runtime metrics, and PM frequency |
| `SM Equipment Maintenance Schedule` | Defines PM tasks, frequency, required spare parts, and assigned technician |
| `SM Breakdown Log` | Records unplanned failures with root cause, remedy, and spare parts consumed |
| `SM Spare Part` | Spare part catalog with criticality, min stock, reorder policy per equipment |
| `SM Equipment Utilization Log` | Daily runtime, idle time, downtime, and utilization % per equipment |

### Functional Flow
```
Equipment master created → linked to Workstation
       │
       └── SM Equipment Maintenance Schedule configured:
               ├── Type: Preventive / Predictive / Calibration / Inspection
               ├── Frequency: Daily / Weekly / Monthly / Runtime Hours
               └── Tasks + required spare parts listed

Daily maintenance check (background job):
       ├── Equipment with next_service_date <= today → maintenance alert
       └── Real-time push notification to Maintenance Engineer

SM Breakdown Log (on failure):
       ├── Equipment status → Breakdown
       ├── breakdown_time recorded
       ├── Technician assigned
       ├── Spare parts consumed logged (from SM Spare Part catalog)
       ├── resumed_time recorded → downtime_hrs computed
       └── Equipment status → Active
```

### OEE Impact
SM Breakdown Log feeds into OEE Availability calculation:
`Availability = (Planned Hours - Downtime) / Planned Hours`

---

## 9. BOM & Engineering Change Management

### Definition
Extends ERPNext's Bill of Materials with formal version control — engineering
change requests (ECR), controlled revisions, material substitution rules, and
multi-level BOM comparison — ensuring manufacturing always uses the approved
and current BOM.

### Key DocTypes
| DocType | Purpose |
|---------|---------|
| `SM Engineering Change Request` | Formal request for BOM change with approval workflow and item-level diff |
| `SM BOM Revision` | Immutable revision record linked to ECR and BOM |
| `SM Material Substitution` | Approved substitute items with conversion factors and validity periods |

### Functional Flow
```
Engineer raises SM Engineering Change Request:
       ├── Links to BOM (current revision shown)
       ├── Describes change (Design / Material Substitution / Process / Documentation)
       ├── Lists SM ECR Item Changes (add / remove / substitute / qty change)
       └── Status: Draft → Under Review

Review & approval:
       ├── Reviewed by → Engineering Manager
       └── Approved by → Production Manager (or configurable workflow)

ECR approved:
       └── BOM updated (new revision auto-numbered: Rev 01, Rev 02, ...)
               ├── sm_revision field on BOM updated
               ├── sm_ecr_reference linked
               └── SM BOM Revision record created (immutable history)

Material Substitution:
       ├── SM Material Substitution created (original → substitute, conversion factor)
       ├── Validity period: valid_from / valid_to
       └── Shop Floor Terminal resolves substitution at time of material issuance
```

### ERPNext Integration Points
- `BOM.on_update` → auto-creates SM BOM Revision when ECR is referenced
- `BOM` — custom fields: `sm_revision`, `sm_ecr_reference`

---

## 10. Analytics

### Definition
Provides operational intelligence through script-based reports and REST API
endpoints — covering OEE, production efficiency, downtime root cause, scrap
analysis, cost variance, and shift productivity — designed for both in-app
dashboards and external BI tool integration.

### Reports
| Report | Key Metrics |
|--------|-------------|
| **OEE Report** | Per-workstation OEE %, efficiency %, downtime, by date and shift |
| **Production Efficiency Report** | Planned vs actual qty, efficiency %, OEE, downtime per work order |
| **Downtime Analysis Report** | Downtime by workstation, type, cause — total hours, event count, averages |
| **Scrap Analysis Report** | Scrap qty and value by item, defect code, workstation — Pareto-ready |
| **Cost Variance Report** | Standard vs actual cost, variance amount and %, per work order |

### OEE Calculation
```
OEE = Availability × Performance × Quality

Availability = (Planned Hours - Downtime Hours) / Planned Hours
Performance  = (Actual Qty × Ideal Cycle Time) / Available Hours
Quality      = Good Qty / Total Qty  (Good = Total - Scrap)

Target benchmarks:
  World-class OEE: ≥ 85%
  Good OEE:        ≥ 65%
  Poor OEE:        < 65%
```

### REST API Endpoints (for BI / External Dashboards)
```
GET  /api/method/smart_manufacturing.api.analytics.get_oee_dashboard
     → { workstation, avg_oee, avg_efficiency, avg_downtime_mins, total_produced, total_scrap }

GET  /api/method/smart_manufacturing.api.analytics.get_production_summary
     → { total_work_orders, total_planned_qty, total_produced_qty, avg_oee, completed, in_process }

GET  /api/method/smart_manufacturing.api.analytics.get_shortage_summary
     → { severity, count, total_shortage }
```
