# REST API Reference

All endpoints are available at:
```
/api/method/smart_manufacturing.api.<module>.<function>
```

Authentication uses Frappe's standard token-based auth:
```
Authorization: token <api_key>:<api_secret>
```

---

## Shop Floor API (`api/shop_floor.py`)

### `GET get_workstation_status`
Returns live status of one or all workstations.

**Parameters:** `workstation` (optional — omit for all)

**Response:**
```json
[
  {
    "name": "WS-001",
    "status": "Production",
    "sm_planned_capacity_hours": 8.0,
    "sm_equipment": "EQ-0001",
    "oee": 78.5,
    "active_jobs": 3
  }
]
```

---

### `POST record_production`
IoT / tablet endpoint to record job card completion.

**Parameters:**
| Name | Required | Description |
|------|----------|-------------|
| `job_card` | Yes | Job Card name |
| `qty_produced` | Yes | Quantity completed |
| `scrap_qty` | No | Scrap quantity (default 0) |
| `operator` | No | Employee name |

**Response:** `{ "status": "success", "job_card": "JC-001", "qty_produced": 50 }`

---

### `POST start_downtime`
Begin a downtime event (machine stops).

**Parameters:** `workstation`, `downtime_type`, `cause_category` (optional), `work_order` (optional)

**Response:** `{ "downtime_log": "DT-00001", "started_at": "2026-05-22 09:15:00" }`

---

### `POST end_downtime`
End a downtime event and compute duration.

**Parameters:** `downtime_log`, `cause_description` (optional), `corrective_action` (optional)

**Response:** `{ "downtime_log": "DT-00001", "downtime_minutes": 23.5 }`

---

### `GET get_pending_qc`
Returns quality inspections awaiting sign-off.

**Response:**
```json
[
  { "name": "QI-001", "item_code": "FG-100", "reference_name": "JC-005", "status": "Draft" }
]
```

---

### `POST scan_barcode`
Resolves a barcode or QR code to a Frappe document.

**Parameters:** `barcode`

**Response:** `{ "type": "Work Order", "name": "WO-0025" }`
*(type can be "Work Order", "Job Card", or "Item")*

---

## Planning API (`api/planning.py`)

### `GET get_capacity_load`
Returns workstation load for a date range.

**Parameters:** `workstation`, `from_date`, `to_date`

**Response:** List of `{ work_order, planned_start_date, planned_end_date, qty }`

---

### `GET get_production_schedule_status`
Returns recent production schedules with capacity summary.

**Parameters:** `company` (optional)

**Response:**
```json
[
  {
    "name": "PS-2026-05-001",
    "title": "Week 21 Schedule",
    "status": "Approved",
    "total_machine_hours": 184.5,
    "bottleneck_detected": 0
  }
]
```

---

### `POST trigger_mrp`
Manually trigger an MRP run (enqueues a background job).

**Response:** `{ "status": "MRP job enqueued" }`

---

## Quality API (`api/quality.py`)

### `GET get_quality_alerts`
Returns quality alerts filtered by status.

**Parameters:** `status` (default: "Open")

**Response:**
```json
[
  {
    "name": "QA-00042",
    "alert_title": "QC Failed — FG-100",
    "severity": "High",
    "item_code": "FG-100",
    "alert_message": "Quality Inspection QI-001 failed.",
    "creation": "2026-05-22 08:30:00"
  }
]
```

---

### `POST acknowledge_alert`
Mark a quality alert as acknowledged.

**Parameters:** `alert_name`

**Response:** `{ "status": "acknowledged" }`

---

### `GET get_capa_summary`
Returns CAPA count by status with overdue counts.

**Response:** `[ { "status": "Open", "count": 5, "overdue": 2 }, ... ]`

---

### `GET get_batch_trace`
Full forward + backward traceability for a batch.

**Parameters:** `batch_no`

**Response:**
```json
{
  "found": true,
  "genealogy": {
    "name": "BG-00001",
    "batch_no": "BATCH-2026-001",
    "item_code": "FG-MILK-1L",
    "work_order": "WO-0042",
    "manufacture_date": "2026-05-20",
    "expiry_date": "2026-06-20"
  },
  "ingredients": [
    { "batch_no": "RM-BATCH-001", "item_code": "RAW-MILK", "qty_used": 1050.0 }
  ],
  "outputs": [
    { "batch_no": "BATCH-2026-001", "item_code": "FG-MILK-1L", "qty": 1000.0 }
  ]
}
```

---

## Analytics API (`api/analytics.py`)

### `GET get_oee_dashboard`
OEE summary per workstation for a date range.

**Parameters:** `company` (optional), `from_date`, `to_date`

**Response:**
```json
[
  {
    "workstation": "WS-001",
    "avg_oee": 78.5,
    "avg_efficiency": 92.3,
    "avg_downtime_mins": 24.0,
    "total_produced": 4500,
    "total_scrap": 45
  }
]
```

---

### `GET get_production_summary`
Overall production KPIs for a company and date range.

**Parameters:** `company`, `from_date`, `to_date`

**Response:**
```json
[
  {
    "total_work_orders": 42,
    "total_planned_qty": 10000.0,
    "total_produced_qty": 9450.0,
    "avg_oee": 76.2,
    "completed": 38,
    "in_process": 4
  }
]
```

---

### `GET get_shortage_summary`
Open material shortage alerts grouped by severity.

**Response:** `[ { "severity": "Critical", "count": 3, "total_shortage": 500.0 }, ... ]`

---

## IoT Integration Notes

For machine data integration (PLCs, SCADA systems):

```
PLC detects machine stop
    │
    └── POST /api/method/smart_manufacturing.api.shop_floor.start_downtime
            { workstation: "WS-001", downtime_type: "Breakdown", cause_category: "Machine Failure" }

PLC detects machine resume
    └── POST /api/method/smart_manufacturing.api.shop_floor.end_downtime
            { downtime_log: "DT-00042", corrective_action: "Belt replaced" }

Production counter increments
    └── POST /api/method/smart_manufacturing.api.shop_floor.record_production
            { job_card: "JC-001", qty_produced: 1, scrap_qty: 0 }
```

All endpoints return standard Frappe JSON response format:
```json
{ "message": <response_payload> }
```

Error responses use HTTP 400/403/500 with:
```json
{ "exc_type": "ValidationError", "exception": "Error message" }
```
