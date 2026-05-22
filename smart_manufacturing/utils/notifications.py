import frappe


def get_notification_config():
    return {
        "for_doctype": {
            "SM Quality Alert":         {"status": ("!=", "Resolved")},
            "SM Material Shortage Alert":{"status": "Open"},
            "SM CAPA":                  {"status": ("in", ["Open", "In Progress"])},
            "SM NCR":                   {"status": ("in", ["Open", "Under Review"])},
        }
    }
