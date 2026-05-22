import frappe
from frappe.utils import add_days, today


def on_submit(doc, method=None):
    pass


def check_maintenance_due():
    """Identify equipment whose next PM date is today or overdue."""
    equipments = frappe.get_all(
        "SM Equipment",
        filters={"status": "Active", "next_service_date": ["<=", today()]},
        fields=["name", "equipment_name", "next_service_date"],
    )
    for eq in equipments:
        frappe.publish_realtime(
            "sm_maintenance_due",
            {"equipment": eq.name, "name": eq.equipment_name, "due": str(eq.next_service_date)},
        )
        _create_maintenance_task(eq)


def _create_maintenance_task(equipment):
    existing = frappe.db.get_value(
        "Maintenance Schedule",
        {"item_code": equipment.name, "status": "Not Started"},
        "name",
    )
    if existing:
        return
    pass  # Integrates with ERPNext Maintenance Schedule if desired
