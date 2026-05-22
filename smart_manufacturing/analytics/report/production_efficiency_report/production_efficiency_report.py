import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "work_order",     "label": "Work Order",      "fieldtype": "Link",    "options": "Work Order", "width": 150},
        {"fieldname": "item_code",      "label": "Item",            "fieldtype": "Link",    "options": "Item",       "width": 140},
        {"fieldname": "planned_qty",    "label": "Planned Qty",     "fieldtype": "Float",   "width": 110},
        {"fieldname": "produced_qty",   "label": "Produced Qty",    "fieldtype": "Float",   "width": 110},
        {"fieldname": "scrap_qty",      "label": "Scrap Qty",       "fieldtype": "Float",   "width": 100},
        {"fieldname": "efficiency_pct", "label": "Efficiency (%)",  "fieldtype": "Percent", "width": 120},
        {"fieldname": "oee",            "label": "OEE (%)",         "fieldtype": "Percent", "width": 100},
        {"fieldname": "downtime_hrs",   "label": "Downtime (hrs)",  "fieldtype": "Float",   "width": 120},
        {"fieldname": "planned_start",  "label": "Planned Start",   "fieldtype": "Date",    "width": 110},
        {"fieldname": "planned_end",    "label": "Planned End",     "fieldtype": "Date",    "width": 110},
        {"fieldname": "status",         "label": "Status",          "fieldtype": "Data",    "width": 100},
    ]


def get_data(filters):
    conditions = "wo.docstatus IN (1, 2)"
    if filters.get("company"):
        conditions += f" AND wo.company = '{filters['company']}'"
    if filters.get("from_date"):
        conditions += f" AND wo.planned_start_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND wo.planned_start_date <= '{filters['to_date']}'"
    if filters.get("workstation"):
        conditions += f" AND wo.workstation = '{filters['workstation']}'"

    return frappe.db.sql(f"""
        SELECT
            wo.name AS work_order,
            wo.production_item AS item_code,
            wo.qty AS planned_qty,
            wo.produced_qty,
            COALESCE(wo.scrap_qty, 0) AS scrap_qty,
            CASE WHEN wo.qty > 0 THEN ROUND(wo.produced_qty / wo.qty * 100, 2) ELSE 0 END AS efficiency_pct,
            COALESCE(wo.sm_oee, 0) AS oee,
            COALESCE((
                SELECT SUM(dtl.downtime_minutes) / 60
                FROM `tabSM Downtime Log` dtl
                WHERE dtl.work_order = wo.name AND dtl.docstatus = 1
            ), 0) AS downtime_hrs,
            wo.planned_start_date AS planned_start,
            wo.planned_end_date AS planned_end,
            wo.status
        FROM `tabWork Order` wo
        WHERE {conditions}
        ORDER BY wo.planned_start_date DESC
        LIMIT 500
    """, as_dict=True)


def get_chart(data):
    if not data:
        return None
    labels = [d.work_order for d in data[:20]]
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Efficiency (%)", "values": [d.efficiency_pct for d in data[:20]]},
                {"name": "OEE (%)",        "values": [d.oee           for d in data[:20]]},
            ],
        },
        "type": "bar",
        "height": 300,
    }
