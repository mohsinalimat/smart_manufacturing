import frappe


def check_maintenance_due():
    from smart_manufacturing.maintenance_equipment.utils.maintenance import check_maintenance_due as _check
    _check()
