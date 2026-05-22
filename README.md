# Smart Manufacturing

**Production-ready Smart Manufacturing App for ERPNext/Frappe**

A scalable, modular, marketplace-ready Frappe application that extends ERPNext manufacturing capabilities for factories, textile industries, process manufacturing, pharmaceutical, automotive, packaging, and industrial SMEs worldwide.

---

## Modules

| Module | Description |
|--------|-------------|
| **Production Planning** | Finite capacity planning, machine-wise scheduling, shift planning, bottleneck detection, production forecasting |
| **Shop Floor Execution** | Real-time job cards, tablet/mobile terminal, barcode/QR scanning, downtime & scrap logging, operator assignment |
| **Manufacturing Costing** | Machine/labor/overhead costing, actual vs standard, variance analysis, production profitability |
| **Quality Management** | Stage-wise QC, CAPA, NCR, inline quality, inspection templates, AQL sampling, ISO-ready workflows |
| **MRP Enhanced** | Demand forecasting, material shortage prediction, safety stock intelligence, procurement recommendations |
| **Batch & Traceability** | Forward/backward batch genealogy, recall management, expiry alerts, serialized production |
| **Subcontract Manufacturing** | Supplier work orders, material issuance tracking, subcontract costing, reconciliation |
| **Maintenance & Equipment** | Preventive/predictive maintenance, breakdown logging, spare parts, utilization tracking |
| **BOM & Engineering** | BOM revisions, ECR workflows, material substitution, BOM comparison |
| **Analytics** | OEE dashboards, downtime analysis, scrap analysis, cost variance, shift productivity reports |

---

## Installation

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/your-org/smart_manufacturing
bench --site your.site install-app smart_manufacturing
bench --site your.site migrate
```

## Requirements

- ERPNext >= 15.0
- Frappe >= 15.0
- Python >= 3.10

---

## Architecture

```
smart_manufacturing/
├── production_planning/     # Finite capacity, scheduling, forecasting
├── shop_floor/              # Terminal, job cards, downtime, scrap
│   └── page/shop_floor_terminal/   # Tablet/mobile UI
├── manufacturing_costing/   # Cost sheets, variance, machine/labor rates
├── quality_management/      # CAPA, NCR, inline QC, alerts
├── mrp_enhanced/            # Demand forecasting, shortage alerts, MRP
├── batch_traceability/      # Genealogy, recall, expiry management
├── subcontract_manufacturing/  # Supplier WOs, material reconciliation
├── maintenance_equipment/   # PM schedules, breakdowns, spare parts
├── bom_engineering/         # ECR, BOM revisions, substitutions
├── analytics/               # OEE reports, dashboards, BI APIs
├── api/                     # REST endpoints for IoT / external systems
├── localization/            # GCC, India, Pakistan, Europe adapters
├── utils/                   # Jinja helpers, notifications
└── setup/                   # Install script, custom fields, roles
```

---

## Key ERPNext Integration Points

| Smart Manufacturing | ERPNext Doctype |
|--------------------|-----------------|
| Production Schedule | Work Order |
| SM Cost Sheet | Job Card, Stock Entry |
| SM Inline QC | Quality Inspection |
| SM Batch Genealogy | Batch, Stock Entry |
| SM Supplier Work Order | Subcontracting Order |
| SM Equipment | Workstation, Maintenance Schedule |
| SM Engineering Change Request | BOM |
| SM Procurement Recommendation | Purchase Order |

---

## REST API

All endpoints available at `/api/method/smart_manufacturing.api.<module>.<method>`:

```
POST /api/method/smart_manufacturing.api.shop_floor.record_production
POST /api/method/smart_manufacturing.api.shop_floor.start_downtime
POST /api/method/smart_manufacturing.api.shop_floor.end_downtime
GET  /api/method/smart_manufacturing.api.analytics.get_oee_dashboard
GET  /api/method/smart_manufacturing.api.quality.get_batch_trace
GET  /api/method/smart_manufacturing.api.planning.get_capacity_load
```

---

## Industry Support

Designed for: **Textile/Garments**, **Food Manufacturing**, **Chemical/Process**, **Pharmaceutical**, **Automotive**, **Industrial Fabrication**, **Packaging**, **General Manufacturing SMEs**

Localization: **GCC (KSA, UAE)**, **India (GST)**, **Pakistan**, **Europe (VAT/ISO)**

---

## License

MIT License — Copyright Smart Manufacturing
