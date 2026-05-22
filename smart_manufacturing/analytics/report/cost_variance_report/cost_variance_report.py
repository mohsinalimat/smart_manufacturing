import frappe


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters), None, get_chart(get_data(filters))


def get_columns():
    return [
        {"fieldname": "cost_sheet",      "label": "Cost Sheet",     "fieldtype": "Link",    "options": "SM Cost Sheet","width": 140},
        {"fieldname": "work_order",      "label": "Work Order",     "fieldtype": "Link",    "options": "Work Order",   "width": 140},
        {"fieldname": "item_code",       "label": "Item",           "fieldtype": "Link",    "options": "Item",         "width": 130},
        {"fieldname": "planned_qty",     "label": "Planned Qty",    "fieldtype": "Float",   "width": 100},
        {"fieldname": "std_total_cost",  "label": "Std Cost",       "fieldtype": "Currency","width": 120},
        {"fieldname": "act_total_cost",  "label": "Actual Cost",    "fieldtype": "Currency","width": 120},
        {"fieldname": "total_variance",  "label": "Variance",       "fieldtype": "Currency","width": 120},
        {"fieldname": "variance_pct",    "label": "Variance (%)",   "fieldtype": "Percent", "width": 110},
        {"fieldname": "status",          "label": "Status",         "fieldtype": "Data",    "width": 90},
    ]


def get_data(filters):
    conditions = "1=1"
    if filters.get("company"):
        conditions += f" AND cs.company = '{filters['company']}'"
    if filters.get("from_date"):
        conditions += f" AND DATE(cs.creation) >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND DATE(cs.creation) <= '{filters['to_date']}'"
    return frappe.db.sql(f"""
        SELECT
            cs.name AS cost_sheet, cs.work_order, cs.item_code,
            cs.planned_qty, cs.std_total_cost, cs.act_total_cost,
            cs.total_variance, cs.variance_pct, cs.status
        FROM `tabSM Cost Sheet` cs
        WHERE {conditions}
        ORDER BY ABS(cs.total_variance) DESC
        LIMIT 500
    """, as_dict=True)


def get_chart(data):
    if not data:
        return None
    top10 = data[:10]
    return {
        "data": {
            "labels": [d.work_order for d in top10],
            "datasets": [
                {"name": "Std Cost",    "values": [d.std_total_cost  for d in top10]},
                {"name": "Actual Cost", "values": [d.act_total_cost  for d in top10]},
            ],
        },
        "type": "bar",
        "height": 300,
    }
