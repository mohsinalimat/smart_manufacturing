"""Quality Management REST API."""
import frappe
from frappe import _


@frappe.whitelist()
def get_quality_alerts(status="Open"):
    return frappe.get_all(
        "SM Quality Alert",
        filters={"status": status},
        fields=["name", "alert_title", "severity", "item_code", "alert_message", "creation"],
        order_by="creation desc",
        limit=50,
    )


@frappe.whitelist()
def acknowledge_alert(alert_name):
    doc = frappe.get_doc("SM Quality Alert", alert_name)
    doc.status = "Acknowledged"
    doc.save(ignore_permissions=True)
    return {"status": "acknowledged"}


@frappe.whitelist()
def get_capa_summary():
    return frappe.db.sql("""
        SELECT
            status,
            COUNT(*) AS count,
            SUM(CASE WHEN target_date < CURDATE() AND status != 'Closed' THEN 1 ELSE 0 END) AS overdue
        FROM `tabSM CAPA`
        WHERE docstatus < 2
        GROUP BY status
    """, as_dict=True)


@frappe.whitelist()
def get_batch_trace(batch_no):
    """Full forward + backward trace for a batch."""
    genealogy = frappe.db.get_value(
        "SM Batch Genealogy",
        {"batch_no": batch_no},
        ["name", "item_code", "work_order", "manufacture_date", "expiry_date"],
        as_dict=True,
    )
    if not genealogy:
        return {"batch_no": batch_no, "found": False}
    parents = frappe.get_all(
        "SM Batch Genealogy Parent",
        filters={"parent": genealogy.name},
        fields=["batch_no", "item_code", "qty_used"],
    )
    children = frappe.get_all(
        "SM Batch Genealogy Child",
        filters={"parent": genealogy.name},
        fields=["batch_no", "item_code", "qty", "customer", "delivery_date"],
    )
    return {
        "found": True,
        "genealogy": genealogy,
        "ingredients": parents,
        "outputs": children,
    }
