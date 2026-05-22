import frappe


def on_submit(doc, method=None):
    _update_shortage_alerts(doc)


def _update_shortage_alerts(po):
    for item in po.items:
        alerts = frappe.get_all(
            "SM Material Shortage Alert",
            filters={"item_code": item.item_code, "status": "Open"},
            pluck="name",
        )
        for alert in alerts:
            frappe.db.set_value("SM Material Shortage Alert", alert, {
                "status": "PO Raised",
                "po_reference": po.name,
            })
