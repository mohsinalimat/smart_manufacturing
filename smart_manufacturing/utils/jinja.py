import frappe


def get_batch_genealogy(batch_no):
    return frappe.db.get_value(
        "SM Batch Genealogy",
        {"batch_no": batch_no},
        ["name", "item_code", "manufacture_date", "expiry_date", "work_order"],
        as_dict=True,
    )


def get_production_summary(work_order):
    return frappe.db.sql("""
        SELECT
            wo.production_item, wo.qty, wo.produced_qty,
            wo.planned_start_date, wo.planned_end_date,
            wo.sm_oee, wo.status
        FROM `tabWork Order` wo
        WHERE wo.name = %s
    """, work_order, as_dict=True)


def get_oee_for_workstation(workstation):
    cached = frappe.cache().hget("sm_oee", workstation)
    if cached:
        return cached
    from smart_manufacturing.analytics.utils.oee import compute_oee
    return compute_oee(workstation, frappe.utils.today())
