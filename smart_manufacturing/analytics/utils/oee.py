import frappe
from frappe.utils import flt, get_datetime, getdate


def compute_oee(workstation, date):
    """
    OEE = Availability × Performance × Quality
    """
    # Planned production time from shift type (default 8h)
    planned_hours = _get_planned_hours(workstation, date)
    if not planned_hours:
        return 0.0

    # Availability = (Planned - Downtime) / Planned
    downtime = _get_downtime_hours(workstation, date)
    available_hours = max(0, planned_hours - downtime)
    availability = available_hours / planned_hours

    # Performance = (Actual Qty × Ideal Cycle Time) / Available Time
    actual_qty, ideal_cycle_time = _get_performance_data(workstation, date)
    if available_hours > 0:
        performance = min(1.0, (actual_qty * ideal_cycle_time) / (available_hours * 3600))
    else:
        performance = 0.0

    # Quality = Good Qty / Total Qty
    total_qty, scrap_qty = _get_quality_data(workstation, date)
    good_qty = total_qty - scrap_qty
    quality = (good_qty / total_qty) if total_qty > 0 else 1.0

    oee = round(availability * performance * quality * 100, 2)

    # Cache and persist to shift log
    frappe.cache().hset("sm_oee", workstation, oee)
    _update_shift_log_oee(workstation, date, availability, performance, quality, oee)
    return oee


def get_current_oee(workstation):
    cached = frappe.cache().hget("sm_oee", workstation)
    if cached is not None:
        return cached
    return compute_oee(workstation, frappe.utils.today())


def _get_planned_hours(workstation, date):
    result = frappe.db.sql("""
        SELECT COALESCE(sm_planned_capacity_hours, 8)
        FROM `tabWorkstation`
        WHERE name = %s
    """, workstation)
    return flt(result[0][0]) if result else 8.0


def _get_downtime_hours(workstation, date):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(downtime_minutes) / 60, 0)
        FROM `tabSM Downtime Log`
        WHERE workstation = %s
          AND DATE(from_time) = %s
          AND docstatus = 1
    """, (workstation, date))
    return flt(result[0][0]) if result else 0.0


def _get_performance_data(workstation, date):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(jc.total_completed_qty), 0)
        FROM `tabJob Card` jc
        WHERE jc.workstation = %s
          AND DATE(jc.modified) = %s
          AND jc.docstatus = 1
    """, (workstation, date))
    actual_qty = flt(result[0][0]) if result else 0
    ideal_cycle_time = 30  # seconds per unit — default; should be item-specific
    return actual_qty, ideal_cycle_time


def _get_quality_data(workstation, date):
    total = frappe.db.sql("""
        SELECT COALESCE(SUM(total_completed_qty), 0)
        FROM `tabJob Card`
        WHERE workstation = %s AND DATE(modified) = %s AND docstatus = 1
    """, (workstation, date))
    scrap = frappe.db.sql("""
        SELECT COALESCE(SUM(scrap_qty), 0)
        FROM `tabSM Scrap Rejection Log`
        WHERE workstation = %s AND DATE(creation) = %s AND docstatus = 1
    """, (workstation, date))
    return flt(total[0][0]) if total else 0, flt(scrap[0][0]) if scrap else 0


def _update_shift_log_oee(workstation, date, availability, performance, quality, oee):
    shift_log = frappe.db.get_value(
        "SM Shift Log",
        {"workstation": workstation, "shift_date": date},
        "name",
    )
    if shift_log:
        frappe.db.set_value("SM Shift Log", shift_log, {
            "oee": oee,
            "efficiency_pct": availability * 100,
        })
