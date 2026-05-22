import frappe


def check_pending_capa():
    from smart_manufacturing.sm_quality_management.utils.quality_inspection import check_pending_capa as _check
    _check()
