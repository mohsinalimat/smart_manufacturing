import frappe
from frappe.utils import flt, add_days, today, getdate


def run_mrp_for_work_orders():
    """Generate shortage alerts for all open work orders."""
    wos = frappe.get_all(
        "Work Order",
        filters={"docstatus": 1, "status": ["not in", ["Completed", "Stopped"]]},
        fields=["name", "production_item", "qty", "planned_start_date", "company"],
    )
    for wo in wos:
        _check_material_availability(wo)


def _check_material_availability(wo):
    bom = frappe.db.get_value("Work Order", wo.name, "bom_no")
    if not bom:
        return
    bom_items = frappe.get_all(
        "BOM Item",
        filters={"parent": bom},
        fields=["item_code", "qty", "uom", "warehouse"],
    )
    for bom_item in bom_items:
        required_qty = flt(bom_item.qty) * flt(wo.qty)
        warehouse = bom_item.warehouse or frappe.db.get_value("Company", wo.company, "default_inventory_account")
        available = _get_stock_qty(bom_item.item_code, warehouse)
        if available < required_qty:
            _create_shortage_alert(
                item_code=bom_item.item_code,
                warehouse=warehouse or "All Warehouses",
                required_qty=required_qty,
                available_qty=available,
                required_by=wo.planned_start_date,
                work_order=wo.name,
            )


def _get_stock_qty(item_code, warehouse):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(actual_qty), 0)
        FROM `tabBin`
        WHERE item_code = %s AND warehouse = %s
    """, (item_code, warehouse))
    return flt(result[0][0]) if result else 0.0


def _create_shortage_alert(item_code, warehouse, required_qty, available_qty, required_by, work_order):
    existing = frappe.db.get_value(
        "SM Material Shortage Alert",
        {"item_code": item_code, "work_order": work_order, "status": "Open"},
        "name",
    )
    if existing:
        return
    shortage_qty = required_qty - available_qty
    severity = "Critical" if shortage_qty > required_qty * 0.5 else "High" if shortage_qty > required_qty * 0.2 else "Medium"
    alert = frappe.get_doc({
        "doctype": "SM Material Shortage Alert",
        "item_code": item_code,
        "warehouse": warehouse,
        "required_qty": required_qty,
        "available_qty": available_qty,
        "shortage_qty": shortage_qty,
        "required_by": required_by,
        "work_order": work_order,
        "severity": severity,
        "status": "Open",
    })
    alert.insert(ignore_permissions=True)
    frappe.publish_realtime(
        "sm_shortage_alert",
        {"item": item_code, "shortage": shortage_qty, "severity": severity},
    )


def compute_dynamic_reorder_point(item_code, warehouse=None):
    policy = frappe.db.get_value(
        "SM Safety Stock Policy",
        {"item_code": item_code},
        ["method", "lead_time_days", "safety_stock_qty", "days_of_supply", "service_level_pct"],
        as_dict=True,
    )
    if not policy:
        return 0
    avg_demand = _compute_avg_daily_demand(item_code)
    lead_time = flt(policy.lead_time_days)
    safety_stock = flt(policy.safety_stock_qty)

    if policy.method == "Days of Supply":
        safety_stock = avg_demand * flt(policy.days_of_supply)
    elif policy.method == "Automatic (Statistical)":
        safety_stock = avg_demand * lead_time * 0.25  # simplified Z-score approx

    reorder_point = avg_demand * lead_time + safety_stock
    frappe.db.set_value("Item", item_code, "sm_reorder_point", reorder_point)
    frappe.db.set_value("SM Safety Stock Policy", {"item_code": item_code}, {
        "avg_daily_demand": avg_demand,
        "reorder_point": reorder_point,
        "last_computed": frappe.utils.now(),
    })
    return reorder_point


def _compute_avg_daily_demand(item_code, days=90):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(sii.qty), 0) / %s
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE sii.item_code = %s
          AND si.docstatus = 1
          AND si.posting_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
    """, (days, item_code, days))
    return flt(result[0][0]) if result else 0.0


def generate_procurement_recommendations():
    """Auto-generate procurement recommendations from shortage alerts."""
    alerts = frappe.get_all(
        "SM Material Shortage Alert",
        filters={"status": "Open"},
        fields=["item_code", "shortage_qty", "required_by", "name"],
    )
    if not alerts:
        return
    rec = frappe.get_doc({
        "doctype": "SM Procurement Recommendation",
        "company": frappe.defaults.get_defaults().get("company"),
        "recommendation_date": today(),
        "status": "Draft",
        "items": [],
    })
    for alert in alerts:
        supplier = frappe.db.get_value(
            "Item Default",
            {"parent": alert.item_code},
            "default_supplier",
        )
        rec.append("items", {
            "item_code": alert.item_code,
            "recommended_qty": alert.shortage_qty,
            "supplier": supplier,
            "required_by": alert.required_by,
        })
    if rec.items:
        rec.insert(ignore_permissions=True)
        return rec.name
