import frappe


def check_capacity_alerts():
    overloaded = frappe.db.sql("""
        SELECT name FROM `tabCapacity Plan`
        WHERE is_overloaded = 1 AND docstatus < 2
    """, as_dict=True)
    for row in overloaded:
        frappe.publish_realtime(
            "sm_capacity_alert",
            {"capacity_plan": row.name, "message": "Workstation is overloaded"},
        )
