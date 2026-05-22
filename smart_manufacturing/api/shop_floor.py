"""
REST API endpoints for Shop Floor — IoT terminals, mobile apps, external systems.
All methods are @frappe.whitelist() and available at:
  POST /api/method/smart_manufacturing.api.shop_floor.<method>
"""
import frappe
from frappe import _
from frappe.utils import flt, now_datetime


@frappe.whitelist()
def get_workstation_status(workstation=None):
    """Return live status of workstation(s)."""
    filters = {}
    if workstation:
        filters["name"] = workstation
    ws_list = frappe.get_all(
        "Workstation",
        filters=filters,
        fields=["name", "status", "sm_planned_capacity_hours", "sm_equipment"],
    )
    result = []
    for ws in ws_list:
        oee = frappe.cache().hget("sm_oee", ws.name) or 0
        active_jobs = frappe.db.count(
            "Job Card",
            {"workstation": ws.name, "status": "Work In Progress", "docstatus": ["<", 2]},
        )
        result.append({**ws, "oee": oee, "active_jobs": active_jobs})
    return result


@frappe.whitelist()
def record_production(job_card, qty_produced, scrap_qty=0, operator=None):
    """IoT / tablet endpoint to record production completion."""
    frappe.has_permission("Job Card", throw=True)
    doc = frappe.get_doc("Job Card", job_card)
    if doc.status not in ("Open", "Work In Progress"):
        frappe.throw(_("Job Card is not in an active state"))

    for log in doc.time_logs:
        if not log.to_time:
            log.to_time = now_datetime()
            log.completed_qty = flt(qty_produced)
            break
    else:
        doc.append("time_logs", {
            "from_time": now_datetime(),
            "to_time": now_datetime(),
            "completed_qty": flt(qty_produced),
            "employee": operator,
        })

    doc.total_completed_qty = flt(qty_produced)
    doc.sm_scrap_qty = flt(scrap_qty)
    if operator:
        doc.sm_operator = operator
    doc.save(ignore_permissions=True)
    return {"status": "success", "job_card": doc.name, "qty_produced": qty_produced}


@frappe.whitelist()
def start_downtime(workstation, downtime_type, cause_category=None, work_order=None):
    """Begin a downtime event (from IoT or operator)."""
    doc = frappe.get_doc({
        "doctype": "SM Downtime Log",
        "workstation": workstation,
        "work_order": work_order,
        "downtime_type": downtime_type,
        "cause_category": cause_category,
        "from_time": now_datetime(),
    })
    doc.insert(ignore_permissions=True)
    return {"downtime_log": doc.name, "started_at": str(doc.from_time)}


@frappe.whitelist()
def end_downtime(downtime_log, cause_description=None, corrective_action=None):
    """End a downtime event and compute duration."""
    doc = frappe.get_doc("SM Downtime Log", downtime_log)
    if doc.to_time:
        frappe.throw(_("Downtime already ended"))
    doc.to_time = now_datetime()
    from frappe.utils import time_diff_in_seconds
    diff = time_diff_in_seconds(doc.to_time, doc.from_time)
    doc.downtime_minutes = round(diff / 60, 2)
    if cause_description:
        doc.cause_description = cause_description
    if corrective_action:
        doc.corrective_action = corrective_action
    doc.save(ignore_permissions=True)
    doc.submit()
    return {"downtime_log": doc.name, "downtime_minutes": doc.downtime_minutes}


@frappe.whitelist()
def get_pending_qc(workstation=None, operator=None):
    """Return QC inspections awaiting sign-off."""
    filters = {"status": ["in", ["Draft", "Initiated"]]}
    return frappe.get_all(
        "Quality Inspection",
        filters=filters,
        fields=["name", "item_code", "reference_name", "reference_type", "status"],
        limit=50,
    )
