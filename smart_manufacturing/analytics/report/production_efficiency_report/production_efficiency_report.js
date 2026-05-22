frappe.query_reports["Production Efficiency Report"] = {
    filters: [
        {fieldname: "company",     label: __("Company"),     fieldtype: "Link",    options: "Company",    reqd: 1, default: frappe.defaults.get_default("company")},
        {fieldname: "from_date",   label: __("From Date"),   fieldtype: "Date",    default: frappe.datetime.month_start()},
        {fieldname: "to_date",     label: __("To Date"),     fieldtype: "Date",    default: frappe.datetime.now_date()},
        {fieldname: "workstation", label: __("Workstation"), fieldtype: "Link",    options: "Workstation"},
        {fieldname: "status",      label: __("Status"),      fieldtype: "Select",
          options: "\nNot Started\nIn Process\nCompleted\nStopped"},
    ]
};
