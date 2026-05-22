import frappe


def run_daily_mrp():
    from smart_manufacturing.mrp_enhanced.utils.mrp import run_mrp_for_work_orders
    run_mrp_for_work_orders()


def run_demand_forecast():
    from smart_manufacturing.mrp_enhanced.utils.mrp import compute_dynamic_reorder_point
    items = frappe.get_all("SM Safety Stock Policy", pluck="item_code")
    for item in items:
        try:
            compute_dynamic_reorder_point(item)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Reorder Point failed: {item}")
