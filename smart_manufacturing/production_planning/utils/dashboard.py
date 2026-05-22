import frappe


def get_data(data):
    return {
        "fieldname": "sm_production_schedule",
        "transactions": [
            {"label": "Production", "items": ["Production Schedule", "Capacity Plan"]},
            {"label": "Shop Floor", "items": ["Job Card", "SM Downtime Log"]},
            {"label": "Costing",    "items": ["SM Cost Sheet"]},
        ],
    }
