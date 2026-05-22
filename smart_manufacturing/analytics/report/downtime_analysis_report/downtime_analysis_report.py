import frappe


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters), None, get_chart(get_data(filters))


def get_columns():
    return [
        {"fieldname": "workstation",      "label": "Workstation",      "fieldtype": "Link",    "options": "Workstation", "width": 150},
        {"fieldname": "downtime_type",    "label": "Downtime Type",    "fieldtype": "Data",    "width": 130},
        {"fieldname": "cause_category",   "label": "Cause",            "fieldtype": "Data",    "width": 140},
        {"fieldname": "total_events",     "label": "Events",           "fieldtype": "Int",     "width": 80},
        {"fieldname": "total_downtime",   "label": "Total (mins)",     "fieldtype": "Float",   "width": 120},
        {"fieldname": "avg_downtime",     "label": "Avg (mins)",       "fieldtype": "Float",   "width": 110},
        {"fieldname": "downtime_hrs",     "label": "Total (hrs)",      "fieldtype": "Float",   "width": 110},
    ]


def get_data(filters):
    conditions = "docstatus = 1"
    if filters.get("workstation"):
        conditions += f" AND workstation = '{filters['workstation']}'"
    if filters.get("from_date"):
        conditions += f" AND DATE(from_time) >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND DATE(from_time) <= '{filters['to_date']}'"
    return frappe.db.sql(f"""
        SELECT
            workstation,
            downtime_type,
            cause_category,
            COUNT(*) AS total_events,
            ROUND(SUM(downtime_minutes), 2) AS total_downtime,
            ROUND(AVG(downtime_minutes), 2) AS avg_downtime,
            ROUND(SUM(downtime_minutes) / 60, 2) AS downtime_hrs
        FROM `tabSM Downtime Log`
        WHERE {conditions}
        GROUP BY workstation, downtime_type, cause_category
        ORDER BY total_downtime DESC
    """, as_dict=True)


def get_chart(data):
    if not data:
        return None
    workstations = list({d.workstation for d in data})[:10]
    return {
        "data": {
            "labels": workstations,
            "datasets": [{"name": "Downtime (hrs)", "values": [
                sum(d.downtime_hrs for d in data if d.workstation == ws) for ws in workstations
            ]}],
        },
        "type": "bar",
        "height": 280,
    }
