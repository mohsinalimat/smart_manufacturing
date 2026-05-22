import frappe


def get_permission_query_conditions(user):
    if "SM Admin" in frappe.get_roles(user) or "System Manager" in frappe.get_roles(user):
        return ""
    return "(`tabProduction Schedule`.company in ({companies}))".format(
        companies=", ".join(
            ["'{}'".format(c) for c in frappe.get_list("Company", pluck="name")]
        )
    )


def has_permission(doc, ptype, user):
    return True
