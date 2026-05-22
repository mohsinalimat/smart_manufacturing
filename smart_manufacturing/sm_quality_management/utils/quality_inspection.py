import frappe


def on_submit(doc, method=None):
    if doc.status == "Rejected":
        _create_ncr(doc)
        _raise_quality_alert(doc)


def on_cancel(doc, method=None):
    pass


def _create_ncr(qi):
    existing = frappe.db.get_value("SM NCR", {"work_order": qi.reference_name}, "name")
    if existing:
        return
    ncr = frappe.get_doc({
        "doctype": "SM NCR",
        "item_code": qi.item_code,
        "work_order": qi.reference_name if qi.reference_type == "Work Order" else None,
        "ncr_date": frappe.utils.today(),
        "nc_description": f"Failed Quality Inspection: {qi.name}",
        "status": "Open",
    })
    ncr.insert(ignore_permissions=True)
    return ncr.name


def _raise_quality_alert(qi):
    alert = frappe.get_doc({
        "doctype": "SM Quality Alert",
        "alert_title": f"QC Failed — {qi.item_code}",
        "severity": "High",
        "item_code": qi.item_code,
        "alert_message": f"Quality Inspection {qi.name} failed. Immediate attention required.",
        "status": "Open",
    })
    alert.insert(ignore_permissions=True)
    frappe.publish_realtime(
        "sm_quality_alert",
        {"alert": alert.name, "item": qi.item_code, "severity": "High"},
    )


def check_pending_capa():
    overdue = frappe.db.sql("""
        SELECT name, title FROM `tabSM CAPA`
        WHERE status IN ('Open', 'In Progress')
          AND target_date < CURDATE()
          AND docstatus < 2
    """, as_dict=True)
    for capa in overdue:
        frappe.publish_realtime(
            "sm_capa_overdue",
            {"capa": capa.name, "title": capa.title},
        )
