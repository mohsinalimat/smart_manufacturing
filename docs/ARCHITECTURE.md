# Architecture Overview

## Design Philosophy

Smart Manufacturing Suite extends ERPNext without modifying its core. Every feature
is built as an additive layer — new DocTypes, hooks into existing events, and custom
fields — so ERPNext upgrades remain safe and backward-compatible.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Smart Manufacturing Suite                       │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Production   │  │  Shop Floor  │  │  Manufacturing Costing   │  │
│  │  Planning    │  │  Execution   │  │  (Standard vs Actual)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘  │
│         │                 │                      │                  │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────────▼───────────────┐  │
│  │  Capacity    │  │  OEE Engine  │  │     Cost Variance &      │  │
│  │  Planner     │  │  (Redis)     │  │     Profitability         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ SM Quality   │  │  MRP Engine  │  │  Batch & Traceability    │  │
│  │ Management   │  │  Enhanced    │  │  (Genealogy + Recall)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Subcontract │  │  Maintenance │  │  BOM & Engineering       │  │
│  │  Mfg         │  │  Equipment   │  │  Change Management       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │          Analytics Layer (OEE · Downtime · Scrap · Cost)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │  hooks  │  events  │  REST API
┌─────────────────────────────▼─────────▼──────────▼─────────────────┐
│                         ERPNext Core                                │
│  Work Order · Job Card · BOM · Stock Entry · Quality Inspection     │
│  Subcontracting Order · Purchase Order · Sales Order · Workstation  │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Dependency Map

```
Production Planning  ──depends on──▶  Work Order (ERPNext)
                                     Workstation (ERPNext)

Shop Floor           ──depends on──▶  Job Card (ERPNext)
                     ──writes to───▶  SM Downtime Log
                                     SM Scrap Rejection Log
                                     SM Shift Log

Manufacturing Costing ─depends on──▶ Work Order, Job Card, Stock Entry
                      ─creates────▶  SM Cost Sheet (on WO submit)

SM Quality Management ─depends on──▶ Quality Inspection (ERPNext)
                      ─creates────▶  SM NCR (on QI reject)
                      ─creates────▶  SM CAPA (on NCR)

MRP Enhanced         ──depends on──▶ BOM, Stock Entry, Purchase Order
                     ──creates────▶  SM Material Shortage Alert
                     ──creates────▶  SM Procurement Recommendation

Batch Traceability   ──depends on──▶ Stock Entry (Manufacture type)
                     ──builds─────▶  SM Batch Genealogy (auto)

Subcontract Mfg      ──depends on──▶ Subcontracting Order (ERPNext)
                     ──creates────▶  SM Supplier Work Order

Maintenance Equipment──standalone──▶ SM Equipment (linked to Workstation)

BOM Engineering      ──depends on──▶ BOM (ERPNext)
                     ──creates────▶  SM BOM Revision (on ECR approval)
```

## Data Flow: Work Order Lifecycle

```
Sales Order / Forecast
        │
        ▼
  Production Schedule ──── Capacity Plan ──── Workstation Schedule
        │                        │
        │ (creates)              │ (validates)
        ▼                        ▼
   Work Order ◄────────── Bottleneck Alert (if overloaded)
        │
        ├──► SM Cost Sheet (standard costs pre-loaded)
        │
        ├──► Job Card(s) ──► Shop Floor Terminal
        │         │                │
        │         │           Operator scans barcode
        │         │                │
        │         ▼                ▼
        │    SM Downtime Log   SM Scrap Rejection Log
        │         │
        │    SM Shift Log (OEE computed hourly)
        │
        ├──► Quality Inspection ──► SM Inline QC
        │              │
        │         (if failed)
        │              ▼
        │          SM NCR ──► SM CAPA ──► SM Quality Alert
        │
        └──► Stock Entry (Manufacture)
                   │
                   ├──► SM Batch Genealogy (auto-built)
                   └──► SM Cost Sheet updated (actual costs)
                              │
                              ▼
                      Variance Report ──► Cost Variance Log
```

## REST API Architecture

```
External Systems / IoT Devices / Mobile Apps
           │
           │  HTTP POST/GET
           ▼
┌──────────────────────────────────────────────────────┐
│              Frappe REST API Gateway                  │
│   /api/method/smart_manufacturing.api.<module>.<fn>  │
└──────────────────────────────────────────────────────┘
           │
    ┌──────┴────────────────────────────┐
    │                                   │
    ▼                                   ▼
api/shop_floor.py               api/analytics.py
  record_production()             get_oee_dashboard()
  start_downtime()                get_production_summary()
  end_downtime()                  get_shortage_summary()
  get_pending_qc()
  scan_barcode()               api/quality.py
                                 get_quality_alerts()
api/planning.py                  acknowledge_alert()
  get_capacity_load()            get_capa_summary()
  get_schedule_status()          get_batch_trace()
  trigger_mrp()
```

## Background Job Architecture

```
Frappe Scheduler
    │
    ├── Hourly Jobs
    │     ├── update_oee_metrics()       → Redis cache per workstation
    │     └── update_wip_costs()         → SM Cost Sheet (open)
    │
    ├── Daily Jobs
    │     ├── run_daily_mrp()            → SM Material Shortage Alert
    │     ├── check_capacity_alerts()    → Real-time push notification
    │     ├── check_maintenance_due()    → Real-time push notification
    │     ├── check_expiry_alerts()      → Batch expiry warnings
    │     └── check_pending_capa()       → CAPA overdue alerts
    │
    ├── Weekly Jobs
    │     ├── run_demand_forecast()      → Dynamic reorder points
    │     └── generate_weekly_reports()  → Analytics summary
    │
    └── Monthly Jobs
          └── close_monthly_costing()   → SM Cost Sheet → Closed
```
