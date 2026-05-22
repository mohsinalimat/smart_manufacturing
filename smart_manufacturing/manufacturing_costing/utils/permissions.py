import frappe


def get_permission_query_conditions(user):
    if "SM Admin" in frappe.get_roles(user) or "System Manager" in frappe.get_roles(user):
        return ""
    return ""


def has_permission(doc, ptype, user):
    return True
