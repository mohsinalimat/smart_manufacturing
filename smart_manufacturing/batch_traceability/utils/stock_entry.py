import frappe
from frappe.utils import flt


def on_submit(doc, method=None):
    if doc.stock_entry_type == "Manufacture":
        _build_genealogy(doc)


def on_cancel(doc, method=None):
    pass


def _build_genealogy(se):
    finished_item = None
    finished_batch = None
    raw_materials = []

    for item in se.items:
        if item.is_finished_item:
            finished_item = item.item_code
            finished_batch = item.batch_no
        else:
            if item.batch_no:
                raw_materials.append(item)

    if not finished_batch:
        return

    existing = frappe.db.get_value("SM Batch Genealogy", {"batch_no": finished_batch}, "name")
    if existing:
        genealogy = frappe.get_doc("SM Batch Genealogy", existing)
    else:
        genealogy = frappe.get_doc({
            "doctype": "SM Batch Genealogy",
            "batch_no": finished_batch,
            "item_code": finished_item,
            "work_order": se.work_order,
            "manufacture_date": se.posting_date,
        })

    for rm in raw_materials:
        genealogy.append("parent_batches", {
            "batch_no": rm.batch_no,
            "item_code": rm.item_code,
            "qty_used": flt(rm.qty),
            "uom": rm.uom,
        })

    genealogy.append("stock_movements", {
        "posting_date": se.posting_date,
        "voucher_type": "Stock Entry",
        "voucher_no": se.name,
        "warehouse": se.to_warehouse,
        "qty": se.fg_completed_qty,
    })

    if existing:
        genealogy.save(ignore_permissions=True)
    else:
        genealogy.insert(ignore_permissions=True)


def check_expiry_alerts():
    near_expiry = frappe.db.sql("""
        SELECT name, item, expiry_date,
               DATEDIFF(expiry_date, CURDATE()) AS days_left
        FROM `tabBatch`
        WHERE expiry_date IS NOT NULL
          AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
          AND COALESCE(stock_quantity, 0) > 0
          AND disabled = 0
    """, as_dict=True)
    for b in near_expiry:
        frappe.publish_realtime(
            "sm_expiry_alert",
            {"batch": b.name, "item": b.item, "days_left": b.days_left},
        )
