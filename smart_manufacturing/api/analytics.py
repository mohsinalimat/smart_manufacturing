"""Analytics REST API for dashboards and external BI tools."""
import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_oee_dashboard(company=None, from_date=None, to_date=None):
    conditions = "1=1"
    if from_date:
        conditions += f" AND sl.shift_date >= '{from_date}'"
    if to_date:
        conditions += f" AND sl.shift_date <= '{to_date}'"
    rows = frappe.db.sql(f"""
        SELECT
            sl.workstation,
            ROUND(AVG(sl.oee), 2)          AS avg_oee,
            ROUND(AVG(sl.efficiency_pct), 2) AS avg_efficiency,
            ROUND(AVG(sl.downtime_minutes), 2) AS avg_downtime_mins,
            SUM(sl.actual_qty)             AS total_produced,
            SUM(sl.scrap_qty)              AS total_scrap
        FROM `tabSM Shift Log` sl
        WHERE {conditions}
        GROUP BY sl.workstation
        ORDER BY avg_oee DESC
    """, as_dict=True)
    return rows


@frappe.whitelist()
def get_production_summary(company=None, from_date=None, to_date=None):
    conditions = "wo.docstatus = 1"
    if company:
        conditions += f" AND wo.company = '{company}'"
    if from_date:
        conditions += f" AND wo.planned_start_date >= '{from_date}'"
    if to_date:
        conditions += f" AND wo.planned_start_date <= '{to_date}'"
    return frappe.db.sql(f"""
        SELECT
            COUNT(*) AS total_work_orders,
            ROUND(SUM(wo.qty), 2) AS total_planned_qty,
            ROUND(SUM(wo.produced_qty), 2) AS total_produced_qty,
            ROUND(AVG(wo.sm_oee), 2) AS avg_oee,
            SUM(CASE WHEN wo.status = 'Completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN wo.status = 'In Process' THEN 1 ELSE 0 END) AS in_process
        FROM `tabWork Order` wo
        WHERE {conditions}
    """, as_dict=True)


@frappe.whitelist()
def get_shortage_summary():
    return frappe.db.sql("""
        SELECT
            severity,
            COUNT(*) AS count,
            ROUND(SUM(shortage_qty), 2) AS total_shortage
        FROM `tabSM Material Shortage Alert`
        WHERE status = 'Open'
        GROUP BY severity
        ORDER BY FIELD(severity, 'Critical', 'High', 'Medium', 'Low')
    """, as_dict=True)
