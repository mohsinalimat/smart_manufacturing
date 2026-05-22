frappe.query_reports["Downtime Analysis Report"] = {
    filters: [
        {fieldname: "workstation", label: __("Workstation"), fieldtype: "Link",  options: "Workstation"},
        {fieldname: "from_date",   label: __("From Date"),   fieldtype: "Date",  default: frappe.datetime.month_start()},
        {fieldname: "to_date",     label: __("To Date"),     fieldtype: "Date",  default: frappe.datetime.now_date()},
        {fieldname: "downtime_type",label: __("Type"),       fieldtype: "Select",
          options: "\nPlanned\nUnplanned\nBreakdown\nChangeover\nQuality Issue\nMaterial Shortage\nOther"},
    ]
};
