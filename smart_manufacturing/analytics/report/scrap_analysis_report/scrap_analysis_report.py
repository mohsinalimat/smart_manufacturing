import frappe


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters), None, get_chart(get_data(filters))


def get_columns():
    return [
        {"fieldname": "item_code",        "label": "Item",           "fieldtype": "Link",    "options": "Item", "width": 140},
        {"fieldname": "workstation",      "label": "Workstation",    "fieldtype": "Link",    "options": "Workstation","width": 140},
        {"fieldname": "rejection_type",   "label": "Rejection Type", "fieldtype": "Data",    "width": 120},
        {"fieldname": "defect_code",      "label": "Defect Code",    "fieldtype": "Data",    "width": 100},
        {"fieldname": "total_events",     "label": "Events",         "fieldtype": "Int",     "width": 80},
        {"fieldname": "total_scrap_qty",  "label": "Scrap Qty",      "fieldtype": "Float",   "width": 100},
        {"fieldname": "total_scrap_value","label": "Scrap Value",    "fieldtype": "Currency","width": 120},
        {"fieldname": "scrap_rate_pct",   "label": "Scrap Rate (%)", "fieldtype": "Percent", "width": 120},
    ]


def get_data(filters):
    conditions = "s.docstatus = 1"
    if filters.get("item_code"):
        conditions += f" AND s.item_code = '{filters['item_code']}'"
    if filters.get("workstation"):
        conditions += f" AND s.workstation = '{filters['workstation']}'"
    if filters.get("from_date"):
        conditions += f" AND DATE(s.creation) >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND DATE(s.creation) <= '{filters['to_date']}'"
    return frappe.db.sql(f"""
        SELECT
            s.item_code,
            s.workstation,
            s.rejection_type,
            s.defect_code,
            COUNT(*) AS total_events,
            ROUND(SUM(s.scrap_qty), 3) AS total_scrap_qty,
            ROUND(COALESCE(SUM(s.scrap_value), 0), 2) AS total_scrap_value,
            ROUND(SUM(s.scrap_qty) / NULLIF((
                SELECT SUM(jc.total_completed_qty)
                FROM `tabJob Card` jc
                WHERE jc.workstation = s.workstation AND jc.docstatus = 1
            ), 0) * 100, 2) AS scrap_rate_pct
        FROM `tabSM Scrap Rejection Log` s
        WHERE {conditions}
        GROUP BY s.item_code, s.workstation, s.rejection_type, s.defect_code
        ORDER BY total_scrap_value DESC
    """, as_dict=True)


def get_chart(data):
    if not data:
        return None
    top10 = data[:10]
    return {
        "data": {
            "labels": [f"{d.item_code} / {d.defect_code or 'N/A'}" for d in top10],
            "datasets": [{"name": "Scrap Qty", "values": [d.total_scrap_qty for d in top10]}],
        },
        "type": "pie",
        "height": 300,
    }
