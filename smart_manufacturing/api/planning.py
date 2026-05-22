"""Production Planning REST API."""
import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_capacity_load(workstation, from_date, to_date):
    from smart_manufacturing.production_planning.utils.capacity import get_workstation_load
    return get_workstation_load(workstation, from_date, to_date)


@frappe.whitelist()
def get_production_schedule_status(company=None):
    filters = {"docstatus": 1}
    if company:
        filters["company"] = company
    schedules = frappe.get_all(
        "Production Schedule",
        filters=filters,
        fields=["name", "title", "planned_start_date", "planned_end_date", "status",
                "total_machine_hours", "bottleneck_detected"],
        order_by="planned_start_date desc",
        limit=20,
    )
    return schedules


@frappe.whitelist()
def trigger_mrp(company=None):
    """Manually trigger MRP run."""
    frappe.has_permission("SM Material Shortage Alert", ptype="create", throw=True)
    frappe.enqueue(
        "smart_manufacturing.mrp_enhanced.utils.mrp.run_mrp_for_work_orders",
        queue="long",
    )
    return {"status": "MRP job enqueued"}
