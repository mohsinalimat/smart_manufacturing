import frappe


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters), None, get_chart(get_data(filters))


def get_columns():
    return [
        {"fieldname": "workstation",  "label": "Workstation",  "fieldtype": "Link",    "options": "Workstation","width": 160},
        {"fieldname": "shift_date",   "label": "Date",         "fieldtype": "Date",    "width": 100},
        {"fieldname": "shift",        "label": "Shift",        "fieldtype": "Link",    "options": "Shift Type", "width": 120},
        {"fieldname": "planned_qty",  "label": "Planned Qty",  "fieldtype": "Float",   "width": 100},
        {"fieldname": "actual_qty",   "label": "Actual Qty",   "fieldtype": "Float",   "width": 100},
        {"fieldname": "scrap_qty",    "label": "Scrap Qty",    "fieldtype": "Float",   "width": 100},
        {"fieldname": "downtime_mins","label": "Downtime (m)", "fieldtype": "Float",   "width": 110},
        {"fieldname": "efficiency_pct","label": "Efficiency %","fieldtype": "Percent", "width": 110},
        {"fieldname": "oee",          "label": "OEE %",        "fieldtype": "Percent", "width": 90},
    ]


def get_data(filters):
    conditions = "1=1"
    if filters.get("workstation"):
        conditions += f" AND sl.workstation = '{filters['workstation']}'"
    if filters.get("from_date"):
        conditions += f" AND sl.shift_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND sl.shift_date <= '{filters['to_date']}'"
    return frappe.db.sql(f"""
        SELECT
            sl.workstation, sl.shift_date, sl.shift,
            sl.planned_qty, sl.actual_qty, sl.scrap_qty,
            sl.downtime_minutes AS downtime_mins,
            sl.efficiency_pct, sl.oee
        FROM `tabSM Shift Log` sl
        WHERE {conditions}
        ORDER BY sl.shift_date DESC, sl.workstation
    """, as_dict=True)


def get_chart(data):
    if not data:
        return None
    ws_oee = {}
    for d in data:
        ws_oee.setdefault(d.workstation, []).append(d.oee or 0)
    labels = list(ws_oee.keys())[:10]
    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Avg OEE (%)", "values": [
                round(sum(ws_oee[ws]) / len(ws_oee[ws]), 2) for ws in labels
            ]}],
        },
        "type": "bar",
        "height": 280,
    }
