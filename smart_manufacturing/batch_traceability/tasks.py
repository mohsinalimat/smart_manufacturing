import frappe


def check_expiry_alerts():
    from smart_manufacturing.batch_traceability.utils.stock_entry import check_expiry_alerts as _check
    _check()
