frappe.query_reports["Cost Variance Report"] = {
    filters: [
        {fieldname: "company",    label: __("Company"),   fieldtype: "Link", options: "Company", reqd: 1, default: frappe.defaults.get_default("company")},
        {fieldname: "from_date",  label: __("From Date"), fieldtype: "Date", default: frappe.datetime.month_start()},
        {fieldname: "to_date",    label: __("To Date"),   fieldtype: "Date", default: frappe.datetime.now_date()},
    ]
};
