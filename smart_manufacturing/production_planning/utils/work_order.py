import frappe
from frappe import _
from frappe.utils import now_datetime, flt


def on_submit(doc, method=None):
    _link_production_schedule(doc)
    _create_cost_sheet(doc)


def on_cancel(doc, method=None):
    _cancel_cost_sheet(doc)


def on_update(doc, method=None):
    _update_schedule_status(doc)


def _link_production_schedule(wo):
    schedule = wo.get("sm_production_schedule")
    if not schedule:
        return
    sched_doc = frappe.get_doc("Production Schedule", schedule)
    for row in sched_doc.work_orders:
        if row.work_order == wo.name:
            row.status = "Scheduled"
    sched_doc.save(ignore_permissions=True)


def _create_cost_sheet(wo):
    if wo.get("sm_cost_sheet"):
        return
    cost_sheet = frappe.get_doc({
        "doctype": "SM Cost Sheet",
        "work_order": wo.name,
        "company": wo.company,
        "item_code": wo.production_item,
        "planned_qty": wo.qty,
        "status": "Open",
    })
    cost_sheet.insert(ignore_permissions=True)
    frappe.db.set_value("Work Order", wo.name, "sm_cost_sheet", cost_sheet.name)


def _cancel_cost_sheet(wo):
    cost_sheet = wo.get("sm_cost_sheet")
    if cost_sheet and frappe.db.exists("SM Cost Sheet", cost_sheet):
        cs = frappe.get_doc("SM Cost Sheet", cost_sheet)
        if cs.docstatus == 1:
            cs.cancel()
        cs.status = "Cancelled"
        cs.save(ignore_permissions=True)


def _update_schedule_status(wo):
    schedule = wo.get("sm_production_schedule")
    if not schedule:
        return
    frappe.enqueue(
        "smart_manufacturing.production_planning.utils.capacity.recalculate_schedule_utilization",
        schedule=schedule,
        queue="short",
    )
