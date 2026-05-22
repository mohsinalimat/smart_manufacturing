import frappe
from frappe.utils import flt, time_diff_in_hours


def on_submit(doc, method=None):
    _update_downtime_total(doc)
    _update_shift_log(doc)
    _trigger_qc_if_needed(doc)


def on_update(doc, method=None):
    _sync_operator_to_assignment(doc)


def on_cancel(doc, method=None):
    pass


def _update_downtime_total(jc):
    total_dt = frappe.db.sql("""
        SELECT COALESCE(SUM(downtime_minutes), 0) FROM `tabSM Downtime Log`
        WHERE work_order = %s AND docstatus = 1
    """, jc.work_order)[0][0]
    frappe.db.set_value("Job Card", jc.name, "sm_downtime_minutes", total_dt)


def _update_shift_log(jc):
    if not jc.sm_operator:
        return
    shift_log = frappe.db.get_value(
        "SM Shift Log",
        {"workstation": jc.workstation, "shift_date": frappe.utils.today()},
        "name",
    )
    if shift_log:
        frappe.db.set_value(
            "SM Shift Log", shift_log, "actual_qty",
            frappe.db.get_value("SM Shift Log", shift_log, "actual_qty") + flt(jc.total_completed_qty),
        )


def _trigger_qc_if_needed(jc):
    wo = frappe.get_doc("Work Order", jc.work_order)
    if wo.quality_inspection_template:
        existing = frappe.db.get_value(
            "Quality Inspection",
            {"reference_name": jc.name, "reference_type": "Job Card"},
            "name",
        )
        if not existing:
            qi = frappe.get_doc({
                "doctype": "Quality Inspection",
                "inspection_type": "In Process",
                "reference_type": "Job Card",
                "reference_name": jc.name,
                "item_code": wo.production_item,
                "quality_inspection_template": wo.quality_inspection_template,
                "sample_size": 1,
            })
            qi.insert(ignore_permissions=True)
            frappe.db.set_value("Job Card", jc.name, "sm_qc_status", "Pending")


def _sync_operator_to_assignment(jc):
    if jc.sm_operator:
        frappe.db.set_value(
            "SM Operator Assignment",
            {"work_order": jc.work_order, "workstation": jc.workstation},
            "status", "Active",
        )


