import frappe
from frappe.utils import flt, get_datetime, date_diff


def recalculate_schedule_utilization(schedule):
    doc = frappe.get_doc("Production Schedule", schedule)
    total_machine = 0.0
    total_labor = 0.0
    for row in doc.work_orders:
        wo = frappe.get_value(
            "Work Order", row.work_order,
            ["planned_start_date", "planned_end_date", "qty"],
            as_dict=True,
        )
        if wo and wo.planned_start_date and wo.planned_end_date:
            days = max(1, date_diff(wo.planned_end_date, wo.planned_start_date))
            machine_h = flt(row.machine_hours) or days * 8
            total_machine += machine_h
            total_labor += machine_h  # rough 1:1 default
    doc.total_machine_hours = total_machine
    doc.total_labor_hours = total_labor
    doc.bottleneck_detected = _detect_bottleneck(doc)
    doc.save(ignore_permissions=True)


def _detect_bottleneck(schedule_doc):
    workstation_hours = {}
    for row in schedule_doc.work_orders:
        ws = row.workstation
        if not ws:
            continue
        workstation_hours.setdefault(ws, 0)
        workstation_hours[ws] += flt(row.machine_hours) or 8
    for ws, hours in workstation_hours.items():
        capacity = frappe.db.get_value("Workstation", ws, "sm_planned_capacity_hours") or 8
        total_days = max(
            1,
            date_diff(schedule_doc.planned_end_date, schedule_doc.planned_start_date),
        )
        if hours > capacity * total_days:
            return 1
    return 0


def get_workstation_load(workstation, from_date, to_date):
    """Return list of {work_order, planned_hours, available_hours} per day."""
    return frappe.db.sql("""
        SELECT
            wo.name AS work_order,
            wo.planned_start_date,
            wo.planned_end_date,
            wo.qty
        FROM `tabWork Order` wo
        WHERE wo.workstation = %(ws)s
          AND wo.planned_start_date >= %(from_date)s
          AND wo.planned_end_date   <= %(to_date)s
          AND wo.docstatus = 1
    """, {"ws": workstation, "from_date": from_date, "to_date": to_date}, as_dict=True)
