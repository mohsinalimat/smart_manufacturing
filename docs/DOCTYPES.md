# DocType Reference

Complete list of all doctypes introduced by Smart Manufacturing Suite,
their fields, relationships, and purpose.

---

## Production Planning Module

### Production Schedule
**Purpose:** Master planning document that sequences work orders across workstations with capacity validation.

| Field | Type | Description |
|-------|------|-------------|
| `title` | Data | Human-readable schedule name |
| `company` | Link → Company | Multi-company support |
| `planned_start_date` | Date | Schedule window start |
| `planned_end_date` | Date | Schedule window end |
| `planning_horizon` | Int | Days ahead to plan (default: 30) |
| `schedule_type` | Select | Finite / Infinite / Machine-wise / Shift-wise |
| `status` | Select | Draft → In Review → Approved → In Progress → Completed |
| `work_orders` | Table | Child: Production Schedule Work Order |
| `total_machine_hours` | Float | Computed: sum of machine hours across all WOs |
| `total_labor_hours` | Float | Computed: sum of labor hours |
| `bottleneck_detected` | Check | Set by background capacity check |

**Relationships:** Links to → Work Order (many), Capacity Plan (one per workstation per period)

---

### Capacity Plan
**Purpose:** Analyzes available vs planned hours for a workstation over a date range.

| Field | Type | Description |
|-------|------|-------------|
| `workstation` | Link → Workstation | Target machine/station |
| `from_date` / `to_date` | Date | Analysis period |
| `available_hours` | Float | Planned capacity per day |
| `efficiency_pct` | Percent | Effective capacity factor (default: 85%) |
| `effective_capacity` | Float | Computed: available × efficiency × days |
| `capacity_details` | Table | Per-day load breakdown |
| `total_planned_hours` | Float | Sum from all linked work orders |
| `utilization_pct` | Percent | total_planned / effective_capacity × 100 |
| `is_overloaded` | Check | True when utilization > 100% |

---

### Shift Plan
**Purpose:** Assigns operators to workstations and shifts for a planning period.

| Field | Type | Description |
|-------|------|-------------|
| `company` | Link → Company | — |
| `from_date` / `to_date` | Date | Planning period |
| `status` | Select | Draft / Active / Closed |
| `shift_assignments` | Table | Child: date, workstation, shift name, operator, work order, planned qty |

---

### Production Forecast
**Purpose:** Demand forecasting document with multiple calculation methods.

| Field | Type | Description |
|-------|------|-------------|
| `forecast_method` | Select | Moving Average / Exponential Smoothing / Sales Order Based / Manual |
| `period` | Select | Weekly / Monthly / Quarterly |
| `forecast_items` | Table | Item, forecast qty, actual qty, variance, variance % |

---

## Shop Floor Module

### SM Downtime Log
**Purpose:** Single downtime event — captures machine stops with cause classification for OEE calculation and root cause analysis.

| Field | Type | Description |
|-------|------|-------------|
| `workstation` | Link → Workstation | Machine that was stopped |
| `work_order` | Link → Work Order | Production order affected |
| `downtime_type` | Select | Planned / Unplanned / Breakdown / Changeover / Quality Issue / Material Shortage / Other |
| `from_time` | Datetime | Downtime start |
| `to_time` | Datetime | Downtime end (blank while ongoing) |
| `downtime_minutes` | Float | Computed: (to_time - from_time) in minutes |
| `cause_category` | Select | Machine Failure / Operator Error / Material Issue / Power Failure / Scheduled Maintenance / Setup / Other |
| `cause_description` | Small Text | Free text root cause |
| `corrective_action` | Small Text | What was done to resume |

**Feeds into:** OEE Availability calculation, Downtime Analysis Report

---

### SM Scrap Rejection Log
**Purpose:** Records every scrap or rejection event at the job card level for cost impact and quality analysis.

| Field | Type | Description |
|-------|------|-------------|
| `work_order` | Link → Work Order | — |
| `job_card` | Link → Job Card | Specific operation |
| `item_code` | Link → Item | Rejected item |
| `workstation` | Link → Workstation | — |
| `scrap_qty` | Float | Quantity scrapped |
| `rejection_type` | Select | Scrap / Rework / Return to Vendor / Quarantine |
| `defect_code` | Data | Short defect identifier (e.g. "DIM-001", "VIS-003") |
| `defect_description` | Small Text | Detailed defect description |
| `scrap_value` | Currency | Computed cost of scrap |
| `salvage_value` | Currency | Recoverable value (if any) |

**Feeds into:** Scrap Analysis Report, SM Cost Sheet actual costs

---

### SM Shift Log
**Purpose:** Daily shift summary — planned vs actual production, OEE, and downtime for a workstation.

| Field | Type | Description |
|-------|------|-------------|
| `shift` | Data | Shift name (e.g. "Morning", "Night") |
| `workstation` | Link → Workstation | — |
| `shift_date` | Date | Production date |
| `supervisor` | Link → Employee | Shift supervisor |
| `planned_qty` | Float | Target for the shift |
| `actual_qty` | Float | Actual produced (updated from job cards) |
| `scrap_qty` | Float | Total scrap in shift |
| `downtime_minutes` | Float | Total downtime (from SM Downtime Log) |
| `efficiency_pct` | Percent | Computed: actual / planned × 100 |
| `oee` | Percent | Computed hourly by OEE engine |

---

## Manufacturing Costing Module

### SM Cost Sheet
**Purpose:** Per-work-order cost breakdown comparing standard (planned) costs against actual costs with variance analysis.

| Field | Type | Description |
|-------|------|-------------|
| `work_order` | Link → Work Order | One cost sheet per work order |
| `item_code` | Link → Item | Finished good being produced |
| `currency` | Link → Currency | Multi-currency support |
| `status` | Select | Open / In Progress / Closed / Cancelled |
| `planned_qty` | Float | From work order |
| `actual_qty` | Float | Produced qty (updated from WO) |
| `std_material_cost` | Currency | From BOM material cost per unit |
| `std_labor_cost` | Currency | From SM Labor Cost Rate × planned hours |
| `std_machine_cost` | Currency | From SM Machine Cost Rate × planned hours |
| `std_overhead_cost` | Currency | From SM Overhead Template |
| `std_total_cost` | Currency | Sum of above |
| `act_material_cost` | Currency | From Stock Entry amounts |
| `act_labor_cost` | Currency | From Job Card time logs × employee rate |
| `act_machine_cost` | Currency | From Job Card time logs × machine rate |
| `act_overhead_cost` | Currency | Template-based or percentage |
| `act_total_cost` | Currency | Sum of actuals |
| `total_variance` | Currency | act_total - std_total |
| `variance_pct` | Percent | variance / std_total × 100 |

---

### SM Machine Cost Rate
**Purpose:** Defines the fully-loaded cost per machine hour for a workstation, broken down by cost component.

| Field | Type | Description |
|-------|------|-------------|
| `workstation` | Link → Workstation | — |
| `effective_from` | Date | Rate validity start |
| `depreciation_rate` | Currency | Machine depreciation per hour |
| `power_rate` | Currency | Electricity cost per hour |
| `maintenance_rate` | Currency | Planned maintenance cost per hour |
| `consumables_rate` | Currency | Oils, filters, etc. per hour |
| `total_rate` | Currency | Sum — the rate used in cost calculations |

---

## SM Quality Management Module

### SM Inline QC
**Purpose:** Stage-specific quality inspection record with parametric evaluation against specifications.

| Field | Type | Description |
|-------|------|-------------|
| `work_order` | Link → Work Order | — |
| `job_card` | Link → Job Card | Specific operation stage |
| `item_code` | Link → Item | Item being inspected |
| `inspection_stage` | Select | Incoming / In Process / Final / Outgoing / Retail Sample |
| `inspector` | Link → Employee | Who performed the inspection |
| `lot_no` | Link → Batch | Batch/lot being inspected |
| `sample_size` | Float | Number of units sampled |
| `inspection_template` | Link → SM Inspection Template | Parameter template |
| `parameters` | Table | Child: SM QC Parameter (actual vs spec per parameter) |
| `overall_status` | Select | Passed / Failed / Conditional Pass |
| `defects_found` | Int | Total defects count |
| `reject_qty` | Float | Units rejected |
| `ncr` | Link → SM NCR | Auto-linked on failure |
| `capa` | Link → SM CAPA | Auto-linked on NCR |

---

### SM CAPA
**Purpose:** Corrective and Preventive Action document tracking root cause analysis and action plan to resolution.

| Field | Type | Description |
|-------|------|-------------|
| `title` | Data | Short CAPA title |
| `capa_type` | Select | Corrective / Preventive |
| `priority` | Select | Critical / High / Medium / Low |
| `status` | Select | Open → In Progress → Verification → Closed |
| `source_type` | Select | Quality Inspection / NCR / Customer Complaint / Internal Audit |
| `problem_statement` | Text Editor | Full problem description |
| `root_cause` | Text Editor | 5-Why or Fishbone analysis |
| `actions` | Table | SM CAPA Action (action, responsible, target date, status) |
| `target_date` | Date | CAPA completion deadline |
| `verified_by` | Link → Employee | Quality manager verification |
| `effectiveness` | Select | Effective / Partially Effective / Not Effective |

---

## MRP Enhanced Module

### SM Material Shortage Alert
**Purpose:** Auto-generated alert when material stock is insufficient for an open work order.

| Field | Type | Description |
|-------|------|-------------|
| `item_code` | Link → Item | Shortage item |
| `warehouse` | Link → Warehouse | Stock location checked |
| `required_qty` | Float | What the work order needs |
| `available_qty` | Float | Current bin qty |
| `shortage_qty` | Float | required - available |
| `required_by` | Date | When material is needed |
| `severity` | Select | Critical (>50% short) / High (>20%) / Medium |
| `status` | Select | Open / PO Raised / Resolved |
| `work_order` | Link → Work Order | Originating demand |
| `po_reference` | Link → Purchase Order | PO raised to cover shortage |

---

## Batch Traceability Module

### SM Batch Genealogy
**Purpose:** Complete genealogy tree of a manufactured batch — ingredients used, outputs produced, and every stock movement.

| Field | Type | Description |
|-------|------|-------------|
| `batch_no` | Link → Batch | The batch being traced |
| `item_code` | Link → Item | Finished good |
| `work_order` | Link → Work Order | Manufacturing origin |
| `manufacture_date` | Date | — |
| `expiry_date` | Date | From Batch master |
| `parent_batches` | Table | SM Batch Genealogy Parent: raw material batches consumed |
| `child_batches` | Table | SM Batch Genealogy Child: batches produced from this |
| `stock_movements` | Table | SM Batch Movement: all stock entries involving this batch |

**API:** `GET /api/method/smart_manufacturing.api.quality.get_batch_trace?batch_no=BATCH-001`

---

## Maintenance Equipment Module

### SM Equipment
**Purpose:** Equipment/machine master record with full lifecycle tracking.

| Field | Type | Description |
|-------|------|-------------|
| `equipment_name` | Data | — |
| `equipment_type` | Select | Machine / Conveyor / Utility / Tool / Vehicle / Other |
| `workstation` | Link → Workstation | Physical location |
| `status` | Select | Active / Under Maintenance / Breakdown / Retired / Idle |
| `manufacturer` / `model` / `serial_no` | Data | Equipment identification |
| `purchase_date` / `warranty_expiry` | Date | Lifecycle dates |
| `total_runtime_hrs` | Float | Accumulated runtime (updated from utilization logs) |
| `last_service_date` / `next_service_date` | Date | Maintenance tracking |
| `pm_frequency_days` | Int | How often PM is required |
| `specifications` | Table | Key-value spec pairs |

---

## BOM Engineering Module

### SM Engineering Change Request
**Purpose:** Formal, auditable request to change a BOM — from initial request through approval to implementation.

| Field | Type | Description |
|-------|------|-------------|
| `title` | Data | Change description |
| `ecr_type` | Select | Design Change / Material Substitution / Process Change / Documentation |
| `priority` | Select | Critical / High / Medium / Low |
| `status` | Select | Draft → Under Review → Approved → Rejected → Implemented |
| `bom` | Link → BOM | Target BOM |
| `current_revision` | Data | Read from BOM.sm_revision |
| `new_revision` | Data | Next revision label |
| `effective_date` | Date | When change takes effect on shop floor |
| `item_changes` | Table | SM ECR Item Change: add / remove / substitute / qty change per item |
| `approved_by` | Link → User | Approval signature |

---

## ERPNext Custom Fields Added

| Doctype | Field | Type | Purpose |
|---------|-------|------|---------|
| Work Order | `sm_production_schedule` | Link → Production Schedule | Links WO to its schedule |
| Work Order | `sm_shift` | Data | Planned shift name |
| Work Order | `sm_cost_sheet` | Link → SM Cost Sheet | Auto-linked on submit |
| Work Order | `sm_oee` | Percent | Current OEE for this WO |
| Job Card | `sm_operator` | Link → Employee | Assigned operator |
| Job Card | `sm_downtime_minutes` | Float | Total downtime for this card |
| Job Card | `sm_scrap_qty` | Float | Scrap recorded at this station |
| Job Card | `sm_qc_status` | Select | QC result: Pending/Passed/Failed |
| BOM | `sm_revision` | Data | Current revision label |
| BOM | `sm_ecr_reference` | Link → SM ECR | Change request that triggered revision |
| Item | `sm_industry_type` | Select | Industry classification |
| Item | `sm_safety_stock` | Float | Minimum safety stock quantity |
| Item | `sm_reorder_point` | Float | Dynamic reorder point (computed) |
| Workstation | `sm_machine_cost_per_hour` | Currency | Machine rate for costing |
| Workstation | `sm_planned_capacity_hours` | Float | Available hours per day |
| Workstation | `sm_equipment` | Link → SM Equipment | Physical equipment master |
