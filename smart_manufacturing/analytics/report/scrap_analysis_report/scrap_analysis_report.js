frappe.query_reports["Scrap Analysis Report"] = {
    filters: [
        {fieldname: "from_date",   label: __("From Date"),   fieldtype: "Date",  default: frappe.datetime.month_start()},
        {fieldname: "to_date",     label: __("To Date"),     fieldtype: "Date",  default: frappe.datetime.now_date()},
        {fieldname: "item_code",   label: __("Item"),        fieldtype: "Link",  options: "Item"},
        {fieldname: "workstation", label: __("Workstation"), fieldtype: "Link",  options: "Workstation"},
    ]
};
