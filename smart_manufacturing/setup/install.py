import frappe


def after_install():
    create_roles()
    create_custom_fields()
    create_default_workspaces()
    frappe.db.commit()


def after_migrate():
    create_custom_fields()
    frappe.db.commit()


def create_roles():
    roles = [
        {"role_name": "SM Admin", "desk_access": 1},
        {"role_name": "SM Production Manager", "desk_access": 1},
        {"role_name": "SM Shop Floor Operator", "desk_access": 1},
        {"role_name": "SM Quality Inspector", "desk_access": 1},
        {"role_name": "SM Planner", "desk_access": 1},
        {"role_name": "SM Cost Accountant", "desk_access": 1},
        {"role_name": "SM Maintenance Engineer", "desk_access": 1},
        {"role_name": "SM Subcontract Manager", "desk_access": 1},
        {"role_name": "SM Viewer", "desk_access": 1},
    ]
    for r in roles:
        if not frappe.db.exists("Role", r["role_name"]):
            doc = frappe.get_doc({"doctype": "Role", **r})
            doc.insert(ignore_permissions=True)


def create_custom_fields():
    """Inject lightweight custom fields into ERPNext standard doctypes."""
    fields = {
        "Work Order": [
            {
                "fieldname": "sm_production_schedule",
                "fieldtype": "Link",
                "options": "Production Schedule",
                "label": "Production Schedule",
                "insert_after": "planned_start_date",
                "in_list_view": 0,
            },
            {
                "fieldname": "sm_shift",
                "fieldtype": "Data",
                "label": "Planned Shift",
                "insert_after": "sm_production_schedule",
            },
            {
                "fieldname": "sm_cost_sheet",
                "fieldtype": "Link",
                "options": "SM Cost Sheet",
                "label": "Cost Sheet",
                "insert_after": "sm_shift",
                "read_only": 1,
            },
            {
                "fieldname": "sm_oee",
                "fieldtype": "Percent",
                "label": "OEE (%)",
                "insert_after": "sm_cost_sheet",
                "read_only": 1,
            },
        ],
        "Job Card": [
            {
                "fieldname": "sm_operator",
                "fieldtype": "Link",
                "options": "Employee",
                "label": "Operator",
                "insert_after": "workstation",
            },
            {
                "fieldname": "sm_downtime_minutes",
                "fieldtype": "Float",
                "label": "Downtime (mins)",
                "insert_after": "sm_operator",
                "read_only": 1,
            },
            {
                "fieldname": "sm_scrap_qty",
                "fieldtype": "Float",
                "label": "Scrap Qty",
                "insert_after": "sm_downtime_minutes",
                "read_only": 1,
            },
            {
                "fieldname": "sm_qc_status",
                "fieldtype": "Select",
                "options": "\nPending\nPassed\nFailed\nConditional Pass",
                "label": "QC Status",
                "insert_after": "sm_scrap_qty",
            },
        ],
        "BOM": [
            {
                "fieldname": "sm_revision",
                "fieldtype": "Data",
                "label": "Revision",
                "insert_after": "is_active",
                "read_only": 1,
            },
            {
                "fieldname": "sm_ecr_reference",
                "fieldtype": "Link",
                "options": "SM Engineering Change Request",
                "label": "ECR Reference",
                "insert_after": "sm_revision",
            },
        ],
        "Item": [
            {
                "fieldname": "sm_industry_type",
                "fieldtype": "Select",
                "options": "\nTextile\nFood\nChemical\nPharmaceutical\nAutomotive\nFabrication\nPackaging\nGeneral",
                "label": "Industry Type",
                "insert_after": "item_group",
            },
            {
                "fieldname": "sm_safety_stock",
                "fieldtype": "Float",
                "label": "Safety Stock Qty",
                "insert_after": "sm_industry_type",
            },
            {
                "fieldname": "sm_reorder_point",
                "fieldtype": "Float",
                "label": "Dynamic Reorder Point",
                "insert_after": "sm_safety_stock",
                "read_only": 1,
            },
        ],
        "Workstation": [
            {
                "fieldname": "sm_machine_cost_per_hour",
                "fieldtype": "Currency",
                "label": "Machine Cost/Hour",
                "insert_after": "hour_rate",
            },
            {
                "fieldname": "sm_planned_capacity_hours",
                "fieldtype": "Float",
                "label": "Planned Capacity (hrs/day)",
                "insert_after": "sm_machine_cost_per_hour",
            },
            {
                "fieldname": "sm_equipment",
                "fieldtype": "Link",
                "options": "SM Equipment",
                "label": "Equipment",
                "insert_after": "sm_planned_capacity_hours",
            },
        ],
    }

    for doctype, field_list in fields.items():
        for field in field_list:
            fname = field["fieldname"]
            if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fname}):
                continue
            cf = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": doctype,
                **field,
            })
            cf.insert(ignore_permissions=True)


def create_default_workspaces():
    pass  # Workspace JSON fixtures handle this
