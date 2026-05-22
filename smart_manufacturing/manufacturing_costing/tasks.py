import frappe


def update_wip_costs():
    open_sheets = frappe.get_all(
        "SM Cost Sheet",
        filters={"status": ["in", ["Open", "In Progress"]]},
        pluck="name",
    )
    for cs_name in open_sheets:
        try:
            from smart_manufacturing.manufacturing_costing.utils.costing import compute_actual_costs
            compute_actual_costs(cs_name)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"WIP Cost Update failed: {cs_name}")


def close_monthly_costing():
    today = frappe.utils.today()
    open_sheets = frappe.get_all(
        "SM Cost Sheet",
        filters={"status": "Open"},
        pluck="name",
    )
    for cs_name in open_sheets:
        frappe.db.set_value("SM Cost Sheet", cs_name, "status", "Closed")
    frappe.db.commit()
