# Changelog

All notable changes to Smart Manufacturing Suite will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-05-22

### Added
#### Production Planning
- `Production Schedule` doctype — finite capacity scheduling with bottleneck detection
- `Capacity Plan` doctype — per-workstation load analysis
- `Shift Plan` doctype — operator-to-workstation shift assignments
- `Production Forecast` doctype — demand forecasting (Moving Average, Sales-based)
- `Workstation Schedule` doctype — daily availability calendar
- `SM Bottleneck Log` doctype — overload detection and tracking

#### Shop Floor Execution
- `SM Downtime Log` doctype — machine downtime with cause classification
- `SM Scrap Rejection Log` doctype — scrap/rejection tracking with defect codes
- `SM Operator Assignment` doctype — operator-workstation-shift linking
- `SM Shift Log` doctype — shift-level KPI summary
- **Shop Floor Terminal** page — mobile/tablet-optimized production terminal with barcode/QR scanning

#### Manufacturing Costing
- `SM Cost Sheet` doctype — actual vs standard cost with full variance breakdown
- `SM Machine Cost Rate` doctype — fully-loaded machine cost per hour
- `SM Overhead Template` doctype — flexible overhead allocation rules
- `SM Labor Cost Rate` doctype — per-designation labor cost rates
- `SM Cost Variance Log` doctype — historical variance records

#### SM Quality Management
- `SM Inline QC` doctype — stage-wise parametric quality inspection
- `SM Inspection Template` doctype — reusable QC parameter templates with AQL
- `SM CAPA` doctype — corrective/preventive action with action plan tracking
- `SM NCR` doctype — non-conformance with disposition workflow
- `SM Quality Alert` doctype — real-time quality alerts with severity

#### MRP Enhanced
- `SM Demand Forecast` doctype — item-level demand forecasting
- `SM Material Shortage Alert` doctype — auto-generated stockout warnings
- `SM Procurement Recommendation` doctype — grouped purchase recommendations
- `SM Safety Stock Policy` doctype — dynamic reorder point calculation

#### Batch & Traceability
- `SM Batch Genealogy` doctype — auto-built forward/backward traceability
- `SM Recall Order` doctype — formal product recall with batch tracking
- `SM Lot Tracking Log` doctype — chronological lot event history

#### Subcontract Manufacturing
- `SM Supplier Work Order` doctype — third-party production tracking
- `SM Subcontract Cost Sheet` doctype — subcontract cost analysis

#### Maintenance & Equipment
- `SM Equipment` doctype — equipment master with runtime metrics
- `SM Equipment Maintenance Schedule` doctype — PM scheduling
- `SM Breakdown Log` doctype — unplanned failure tracking
- `SM Spare Part` doctype — spare parts catalog with reorder rules
- `SM Equipment Utilization Log` doctype — daily runtime tracking

#### BOM & Engineering Change Management
- `SM Engineering Change Request` doctype — formal ECR with approval workflow
- `SM BOM Revision` doctype — immutable BOM revision history
- `SM Material Substitution` doctype — approved substitute items

#### Analytics
- **Production Efficiency Report** — planned vs actual with OEE per work order
- **Downtime Analysis Report** — root cause analysis by workstation and cause
- **Scrap Analysis Report** — defect Pareto by item and workstation
- **Cost Variance Report** — standard vs actual cost comparison
- **OEE Report** — availability, performance, quality metrics by shift

#### Infrastructure
- REST API — 4 modules (shop_floor, planning, quality, analytics)
- Real-time WebSocket alerts — quality, shortage, capacity, maintenance, expiry
- Scheduled background jobs — hourly OEE, daily MRP, weekly forecast, monthly close
- ERPNext custom fields — Work Order, Job Card, BOM, Item, Workstation
- 9 roles — SM Admin, Production Manager, Shop Floor Operator, Quality Inspector, Planner, Cost Accountant, Maintenance Engineer, Subcontract Manager, Viewer
- Localization stubs — GCC, India, Pakistan, Europe
