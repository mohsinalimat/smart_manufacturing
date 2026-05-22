import frappe
from frappe.utils import flt, now_datetime, get_datetime, date_diff


def update_oee_metrics():
    """Hourly OEE computation for each active workstation."""
    active_ws = frappe.db.sql("""
        SELECT DISTINCT workstation FROM `tabJob Card`
        WHERE status = 'Work In Progress' AND docstatus < 2
    """, as_dict=True)
    for row in active_ws:
        _compute_oee(row.workstation)


def _compute_oee(workstation):
    from smart_manufacturing.analytics.utils.oee import compute_oee
    oee = compute_oee(workstation, frappe.utils.today())
    frappe.cache().hset("sm_oee", workstation, oee)
