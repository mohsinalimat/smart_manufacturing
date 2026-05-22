/* Smart Manufacturing Suite — Global JS */

frappe.ready(function() {
    if (!frappe.session.user || frappe.session.user === "Guest") return;

    // Real-time quality alerts
    frappe.realtime.on("sm_quality_alert", function(data) {
        frappe.show_alert({
            message: __("Quality Alert: {0} — Severity: {1}", [data.item, data.severity]),
            indicator: data.severity === "Critical" ? "red" : "orange",
        }, 8);
    });

    // Shortage alerts
    frappe.realtime.on("sm_shortage_alert", function(data) {
        frappe.show_alert({
            message: __("Material Shortage: {0} — {1} units short [{2}]", [data.item, data.shortage, data.severity]),
            indicator: data.severity === "Critical" ? "red" : "orange",
        }, 6);
    });

    // Capacity overload
    frappe.realtime.on("sm_capacity_alert", function(data) {
        frappe.show_alert({
            message: __("Capacity Alert: {0} is overloaded", [data.capacity_plan]),
            indicator: "orange",
        }, 5);
    });

    // Maintenance due
    frappe.realtime.on("sm_maintenance_due", function(data) {
        frappe.show_alert({
            message: __("Maintenance Due: {0} — Due: {1}", [data.name, data.due]),
            indicator: "yellow",
        }, 5);
    });

    // CAPA overdue
    frappe.realtime.on("sm_capa_overdue", function(data) {
        frappe.show_alert({
            message: __("CAPA Overdue: {0}", [data.title]),
            indicator: "red",
        }, 6);
    });

    // Expiry alerts
    frappe.realtime.on("sm_expiry_alert", function(data) {
        frappe.show_alert({
            message: __("Batch Expiry: {0} ({1}) expires in {2} days", [data.batch, data.item, data.days_left]),
            indicator: "orange",
        }, 6);
    });
});

// Utility: format OEE with color coding
window.sm_format_oee = function(oee) {
    oee = parseFloat(oee) || 0;
    let color = oee >= 85 ? "#28a745" : oee >= 65 ? "#ffc107" : "#dc3545";
    return `<span style="color:${color};font-weight:600;">${oee.toFixed(1)}%</span>`;
};
