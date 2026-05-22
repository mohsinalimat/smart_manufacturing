import frappe


def on_update(doc, method=None):
    _sync_revision(doc)


def on_submit(doc, method=None):
    pass


def on_cancel(doc, method=None):
    pass


def _sync_revision(bom_doc):
    ecr = bom_doc.get("sm_ecr_reference")
    revision = bom_doc.get("sm_revision")
    if ecr and not revision:
        rev_no = frappe.db.count("SM BOM Revision", {"bom": bom_doc.name}) + 1
        rev_label = f"Rev {rev_no:02d}"
        frappe.db.set_value("BOM", bom_doc.name, "sm_revision", rev_label)
        bom_rev = frappe.get_doc({
            "doctype": "SM BOM Revision",
            "bom": bom_doc.name,
            "revision": rev_label,
            "ecr": ecr,
            "revision_date": frappe.utils.today(),
        })
        bom_rev.insert(ignore_permissions=True)


def get_data(data):
    return {
        "fieldname": "bom",
        "transactions": [
            {"label": "Engineering Changes", "items": ["SM Engineering Change Request", "SM BOM Revision"]},
            {"label": "Substitutions",       "items": ["SM Material Substitution"]},
        ],
    }
