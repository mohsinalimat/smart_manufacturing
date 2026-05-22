app_name = "smart_manufacturing"
app_title = "Smart Manufacturing"
app_publisher = "Smart Manufacturing"
app_description = "Production-ready Smart Manufacturing Suite for ERPNext/Frappe — advanced shop floor, costing, quality, MRP, and analytics for factories worldwide."
app_email = "info@smartmanufacturing.io"
app_license = "MIT"
app_version = "1.0.0"
app_logo_url = "/assets/smart_manufacturing/images/sm_logo.png"

required_apps = ["frappe", "erpnext"]

# --------------------------------------------------------------------------- #
#  Assets
# --------------------------------------------------------------------------- #
app_include_css = "/assets/smart_manufacturing/css/sm.css"
app_include_js  = "/assets/smart_manufacturing/js/sm.js"

web_include_css = "/assets/smart_manufacturing/css/sm.css"
web_include_js  = "/assets/smart_manufacturing/js/sm.js"

# --------------------------------------------------------------------------- #
#  Fixtures
# --------------------------------------------------------------------------- #
fixtures = [
    {"dt": "Custom Field", "filters": [["fieldname", "like", "sm_%"]]},
    {"dt": "Role", "filters": [["role_name", "in", [
        "SM Admin",
        "SM Production Manager",
        "SM Shop Floor Operator",
        "SM Quality Inspector",
        "SM Planner",
        "SM Cost Accountant",
        "SM Maintenance Engineer",
        "SM Subcontract Manager",
        "SM Viewer",
    ]]]},
    {"dt": "Notification", "filters": [["module", "=", "Smart Manufacturing"]]},
]

# --------------------------------------------------------------------------- #
#  DocType Events
# --------------------------------------------------------------------------- #
doc_events = {
    # ------------------------------------------------------------------ #
    #  ERPNext Work Order — hook into job card & costing
    # ------------------------------------------------------------------ #
    "Work Order": {
        "on_submit":  "smart_manufacturing.production_planning.utils.work_order.on_submit",
        "on_cancel":  "smart_manufacturing.production_planning.utils.work_order.on_cancel",
        "on_update":  "smart_manufacturing.production_planning.utils.work_order.on_update",
    },
    "Job Card": {
        "on_submit":  "smart_manufacturing.shop_floor.utils.job_card.on_submit",
        "on_update":  "smart_manufacturing.shop_floor.utils.job_card.on_update",
        "on_cancel":  "smart_manufacturing.shop_floor.utils.job_card.on_cancel",
    },
    # ------------------------------------------------------------------ #
    #  Quality Inspection — extend for inline QC
    # ------------------------------------------------------------------ #
    "Quality Inspection": {
        "on_submit":  "smart_manufacturing.sm_quality_management.utils.quality_inspection.on_submit",
        "on_cancel":  "smart_manufacturing.sm_quality_management.utils.quality_inspection.on_cancel",
    },
    # ------------------------------------------------------------------ #
    #  BOM — trigger engineering change tracking
    # ------------------------------------------------------------------ #
    "BOM": {
        "on_update":  "smart_manufacturing.bom_engineering.utils.bom.on_update",
        "on_submit":  "smart_manufacturing.bom_engineering.utils.bom.on_submit",
        "on_cancel":  "smart_manufacturing.bom_engineering.utils.bom.on_cancel",
    },
    # ------------------------------------------------------------------ #
    #  Stock Entry — batch traceability & cost actuals
    # ------------------------------------------------------------------ #
    "Stock Entry": {
        "on_submit":  "smart_manufacturing.batch_traceability.utils.stock_entry.on_submit",
        "on_cancel":  "smart_manufacturing.batch_traceability.utils.stock_entry.on_cancel",
    },
    # ------------------------------------------------------------------ #
    #  Subcontract Order — supplier work order sync
    # ------------------------------------------------------------------ #
    "Subcontracting Order": {
        "on_submit":  "smart_manufacturing.subcontract_manufacturing.utils.subcontracting_order.on_submit",
        "on_cancel":  "smart_manufacturing.subcontract_manufacturing.utils.subcontracting_order.on_cancel",
    },
    # ------------------------------------------------------------------ #
    #  Purchase Order — MRP procurement tracking
    # ------------------------------------------------------------------ #
    "Purchase Order": {
        "on_submit":  "smart_manufacturing.mrp_enhanced.utils.purchase_order.on_submit",
    },
    # ------------------------------------------------------------------ #
    #  Maintenance — equipment runtime
    # ------------------------------------------------------------------ #
    "Maintenance Schedule": {
        "on_submit":  "smart_manufacturing.maintenance_equipment.utils.maintenance.on_submit",
    },
}

# --------------------------------------------------------------------------- #
#  Scheduled Tasks (background jobs)
# --------------------------------------------------------------------------- #
scheduler_events = {
    "daily": [
        "smart_manufacturing.mrp_enhanced.tasks.run_daily_mrp",
        "smart_manufacturing.production_planning.tasks.check_capacity_alerts",
        "smart_manufacturing.maintenance_equipment.tasks.check_maintenance_due",
        "smart_manufacturing.batch_traceability.tasks.check_expiry_alerts",
        "smart_manufacturing.sm_quality_management.tasks.check_pending_capa",
    ],
    "hourly": [
        "smart_manufacturing.shop_floor.tasks.update_oee_metrics",
        "smart_manufacturing.manufacturing_costing.tasks.update_wip_costs",
    ],
    "weekly": [
        "smart_manufacturing.mrp_enhanced.tasks.run_demand_forecast",
        "smart_manufacturing.analytics.tasks.generate_weekly_reports",
    ],
    "monthly": [
        "smart_manufacturing.manufacturing_costing.tasks.close_monthly_costing",
    ],
}

# --------------------------------------------------------------------------- #
#  Permissions
# --------------------------------------------------------------------------- #
permission_query_conditions = {
    "Production Schedule":       "smart_manufacturing.production_planning.utils.permissions.get_permission_query_conditions",
    "SM Cost Sheet":             "smart_manufacturing.manufacturing_costing.utils.permissions.get_permission_query_conditions",
    "SM Inline QC":              "smart_manufacturing.sm_quality_management.utils.permissions.get_permission_query_conditions",
    "SM Supplier Work Order":    "smart_manufacturing.subcontract_manufacturing.utils.permissions.get_permission_query_conditions",
}

has_permission = {
    "Production Schedule":       "smart_manufacturing.production_planning.utils.permissions.has_permission",
    "SM Cost Sheet":             "smart_manufacturing.manufacturing_costing.utils.permissions.has_permission",
}

# --------------------------------------------------------------------------- #
#  REST API — white-listed methods (see api/ directory)
# --------------------------------------------------------------------------- #
# All @frappe.whitelist() methods in smart_manufacturing/api/ are auto-exposed

# --------------------------------------------------------------------------- #
#  Override Standard Form Scripts
# --------------------------------------------------------------------------- #
override_doctype_dashboards = {
    "Work Order":  "smart_manufacturing.production_planning.utils.dashboard.get_data",
    "BOM":         "smart_manufacturing.bom_engineering.utils.dashboard.get_data",
    "Item":        "smart_manufacturing.batch_traceability.utils.dashboard.get_data",
}

# --------------------------------------------------------------------------- #
#  Notifications
# --------------------------------------------------------------------------- #
notification_config = "smart_manufacturing.utils.notifications.get_notification_config"

# --------------------------------------------------------------------------- #
#  After App Install
# --------------------------------------------------------------------------- #
after_install = "smart_manufacturing.setup.install.after_install"
after_migrate = "smart_manufacturing.setup.install.after_migrate"

# --------------------------------------------------------------------------- #
#  Jinja / Print Format globals
# --------------------------------------------------------------------------- #
jinja = {
    "methods": [
        "smart_manufacturing.utils.jinja.get_batch_genealogy",
        "smart_manufacturing.utils.jinja.get_production_summary",
        "smart_manufacturing.utils.jinja.get_oee_for_workstation",
    ]
}
