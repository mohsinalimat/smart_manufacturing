import frappe


def on_submit(doc, method=None):
    _create_supplier_work_order(doc)


def on_cancel(doc, method=None):
    _cancel_supplier_work_orders(doc)


def _create_supplier_work_order(sc_order):
    for item in sc_order.items:
        existing = frappe.db.get_value(
            "SM Supplier Work Order",
            {"subcontracting_order": sc_order.name, "item_code": item.item_code},
            "name",
        )
        if existing:
            continue
        swo = frappe.get_doc({
            "doctype": "SM Supplier Work Order",
            "supplier": sc_order.supplier,
            "subcontracting_order": sc_order.name,
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.stock_uom,
            "planned_start": sc_order.schedule_date,
            "status": "Draft",
        })
        swo.insert(ignore_permissions=True)


def _cancel_supplier_work_orders(sc_order):
    swos = frappe.get_all(
        "SM Supplier Work Order",
        filters={"subcontracting_order": sc_order.name, "docstatus": 1},
        pluck="name",
    )
    for swo in swos:
        frappe.get_doc("SM Supplier Work Order", swo).cancel()
