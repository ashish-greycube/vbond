// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

let fiscal_year =  erpnext.utils.get_fiscal_year(frappe.datetime.get_today())
frappe.db.get_value("Fiscal Year", fiscal_year, 'year_start_date')
	.then(r => {
		frappe.query_report.set_filter_value("from_date", r.message.year_start_date) 
	})

frappe.query_reports["Customer vs Item Report"] = {
	"filters": [
		{
			fieldname : "from_date",
			fieldtype : 'Date',
			label : __('From Date'),
			reqd : 1, 
		},
		{
			fieldname : "to_date",
			fieldtype : 'Date',
			label : __('To Date'),
			reqd : 1,
			default: 'Today'
		},
		{
			fieldname : "customer_group",
			fieldtype : 'Link',
			label : __('Customer Group'),
			options : 'Customer Group'
		},
		{
			fieldname : "customer",
			fieldtype : 'Link',
			label : __('Customer'),
			options : 'Customer'
		},
		{
			fieldname : "item_group",
			fieldtype : 'Link',
			label : __('Item Group'),
			options : 'Item Group'
		},
		{
			fieldname : "item_name",
			fieldtype : 'Link',
			label : __('Item Name'),
			options : 'Item'
		},
	]
};
