import frappe


def generate_weekly_reports():
    frappe.logger().info("SM Analytics: Weekly report generation triggered")
