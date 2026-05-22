# Smart Manufacturing Suite — Roadmap

## MVP (Phase 1 — Weeks 1–6)

### Week 1–2: Foundation
- [x] App scaffold, hooks, modules, roles
- [x] ERPNext Work Order / Job Card / BOM custom fields
- [x] Setup install script (roles, custom fields)

### Week 3–4: Shop Floor & Planning
- [x] Production Schedule doctype (finite capacity)
- [x] Capacity Plan doctype
- [x] Shift Plan doctype
- [x] SM Downtime Log
- [x] SM Scrap Rejection Log
- [x] SM Operator Assignment
- [x] SM Shift Log
- [x] Shop Floor Terminal page (tablet/mobile UI)
- [x] Barcode / QR scan endpoint

### Week 5–6: Costing & Quality
- [x] SM Cost Sheet (actual vs standard)
- [x] SM Machine Cost Rate
- [x] SM Overhead Template
- [x] SM Inline QC
- [x] SM CAPA / NCR / Quality Alert
- [x] SM Inspection Template
- [x] Auto-create QC from Job Card submission

---

## Phase 2 — Weeks 7–12

### MRP & Materials
- [x] SM Demand Forecast
- [x] SM Material Shortage Alert (auto-generated daily)
- [x] SM Procurement Recommendation
- [x] SM Safety Stock Policy with dynamic reorder point

### Traceability
- [x] SM Batch Genealogy (auto-built on Stock Entry)
- [x] SM Recall Order
- [x] SM Lot Tracking Log
- [x] Expiry alerts (30-day warning)

### Subcontracting
- [x] SM Supplier Work Order (auto-created from Subcontracting Order)
- [x] SM Subcontract Cost Sheet
- [ ] Material issuance Stock Entry automation
- [ ] FG receipt reconciliation report

### BOM Engineering
- [x] SM Engineering Change Request (with approval workflow)
- [x] SM BOM Revision (auto-created on ECR approval)
- [x] SM Material Substitution
- [ ] BOM comparison tool (report)

---

## Phase 3 — Weeks 13–18

### Analytics & Dashboards
- [x] OEE computation (Availability × Performance × Quality)
- [x] Production Efficiency Report
- [x] Downtime Analysis Report
- [x] Scrap Analysis Report
- [x] Cost Variance Report
- [x] OEE Report
- [ ] Shift Productivity Report
- [ ] Number Cards for workspace dashboard
- [ ] Chart.js dashboards for OEE trend
- [ ] Machine Utilization heatmap

### Maintenance & Equipment
- [x] SM Equipment master
- [x] SM Equipment Maintenance Schedule
- [x] SM Breakdown Log
- [x] SM Spare Part catalog
- [x] SM Equipment Utilization Log
- [ ] Predictive maintenance triggers (runtime-based)
- [ ] Spare part auto-PO on breakdown

---

## Enterprise Scaling (Phase 4+)

### Multi-Site & Multi-Company
- [ ] Company-wise permission boundaries
- [ ] Inter-company transfer workflows
- [ ] Consolidated OEE dashboard across plants

### IoT Integration
- [ ] MQTT / WebSocket endpoint for machine data
- [ ] PLC signal → Downtime Log automation
- [ ] Real-time production counter from IoT sensors
- [ ] Machine runtime tracking via IoT

### Advanced Planning
- [ ] Genetic algorithm-based scheduling optimizer
- [ ] Constraint-based MRP (capacity-aware)
- [ ] Visual Gantt chart for production schedule
- [ ] What-if scenario planning

### Industry-Specific Workflows
- [ ] Textile: style/color-wise production tracking, cut-plan integration
- [ ] Food: lot recall simulation, allergen tracking
- [ ] Pharma: batch release workflow, DEA compliance hooks
- [ ] Automotive: PPAP documentation workflow

### Localization Modules
- [ ] GCC: ZATCA e-invoice fields, Arabic print formats
- [ ] India: HSN codes on BOM, GST on services
- [ ] Pakistan: Sales Tax on job work, EOBI payroll link
- [ ] Europe: ISO 9001 audit trail, GDPR data retention rules

### Mobile App (PWA)
- [ ] Offline-capable Shop Floor Terminal
- [ ] Push notifications for alerts
- [ ] Camera-based barcode scanning (no external scanner)
- [ ] Mobile-first CAPA resolution workflow

---

## Performance Optimization Strategy

| Area | Strategy |
|------|----------|
| Large datasets | Index on `work_order`, `workstation`, `posting_date`, `batch_no` |
| OEE computation | Redis cache (hourly update, not per-request) |
| MRP run | Background job (`queue=long`), never on-request |
| Reports | Use `frappe.db.sql()` with explicit joins, avoid ORM for large aggregations |
| Shop Floor Terminal | Pagination (limit 50 job cards), WebSocket for live updates |
| Batch genealogy | Materialized view pattern — pre-build on stock entry, not on query |
| Cost computation | Incremental (hourly WIP update), not full recalculation each time |

---

## Marketplace Deployment

### Frappe Cloud Marketplace Checklist
- [x] `setup.py` with metadata
- [x] `README.md` with installation instructions
- [x] MIT License
- [x] `requirements.txt`
- [ ] App logo (512×512 PNG) at `public/images/sm_logo.png`
- [ ] Frappe Cloud listing page content
- [ ] Demo site / demo credentials
- [ ] Changelog / release notes
- [ ] Unit tests (`frappe.tests.unittest`)
- [ ] CI/CD pipeline (GitHub Actions)

### GitHub Repository Structure (Recommended)
```
smart_manufacturing/
├── .github/workflows/ci.yml
├── .github/workflows/release.yml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── ROADMAP.md
├── requirements.txt
├── setup.py
└── smart_manufacturing/
    └── ... (app code)
```

### Versioning Strategy
- Semantic versioning: `MAJOR.MINOR.PATCH`
- `1.x.x` — ERPNext v15 compatible
- `2.x.x` — ERPNext v16 compatible (future)
- Patch releases for bug fixes only
- Minor releases for new features
- Breaking changes only on major versions

---

## Architecture Decision Records

| Decision | Rationale |
|----------|-----------|
| No ERPNext core modifications | Marketplace compatibility, upgrade safety |
| SM-prefixed doctypes | Avoid naming conflicts with ERPNext standard doctypes |
| `sm_` prefix on all custom fields | Namespaced, easy fixture export, safe upgrade |
| Redis cache for OEE | Sub-millisecond read for terminal display |
| Background MRP job | Never block UI, allow large dataset processing |
| Separate costing module | Decoupled from shop floor — Cost Accountant can work independently |
| Quality module renamed to SM Quality Management | Avoids conflict with ERPNext's Quality Management module |
| Shift Type as Data field | HRMS not required as dependency |
