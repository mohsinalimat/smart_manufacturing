import frappe


@frappe.whitelist()
def get_active_job_cards(workstation=None, operator=None):
    filters = {"docstatus": ["<", 2], "status": ["in", ["Work In Progress", "Open"]]}
    if workstation:
        filters["workstation"] = workstation
    return frappe.get_list(
        "Job Card",
        filters=filters,
        fields=["name", "work_order", "operation", "workstation", "for_quantity",
                "total_completed_qty", "status", "sm_operator", "sm_qc_status"],
        order_by="creation asc",
        limit=50,
    )


@frappe.whitelist()
def start_job_card(job_card, operator=None):
    doc = frappe.get_doc("Job Card", job_card)
    if doc.status == "Open":
        doc.append("time_logs", {"from_time": frappe.utils.now_datetime(), "employee": operator})
        if operator:
            doc.sm_operator = operator
        doc.status = "Work In Progress"
        doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def complete_job_card(job_card, qty_completed, scrap_qty=0):
    doc = frappe.get_doc("Job Card", job_card)
    for log in doc.time_logs:
        if not log.to_time:
            log.to_time = frappe.utils.now_datetime()
            log.completed_qty = qty_completed
            break
    doc.total_completed_qty = qty_completed
    doc.sm_scrap_qty = scrap_qty
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def log_downtime(workstation, downtime_type, cause_category, from_time, work_order=None):
    doc = frappe.get_doc({
        "doctype": "SM Downtime Log",
        "workstation": workstation,
        "work_order": work_order,
        "downtime_type": downtime_type,
        "cause_category": cause_category,
        "from_time": from_time,
    })
    doc.insert(ignore_permissions=True)
    return doc.name


@frappe.whitelist()
def scan_barcode(barcode):
    """Resolve barcode to Work Order, Job Card, or Item."""
    result = {}
    # Check Work Order
    wo = frappe.db.get_value("Work Order", {"name": barcode}, "name")
    if wo:
        result = {"type": "Work Order", "name": wo}
    # Check Job Card
    jc = frappe.db.get_value("Job Card", {"name": barcode}, "name")
    if jc:
        result = {"type": "Job Card", "name": jc}
    # Check Item barcode
    item = frappe.db.get_value("Item Barcode", {"barcode": barcode}, "parent")
    if item:
        result = {"type": "Item", "name": item}
    return result
