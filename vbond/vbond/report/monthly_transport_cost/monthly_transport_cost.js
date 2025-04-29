// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

var date  = new Date()
frappe.query_reports["Monthly Transport Cost"] = {
	"filters": [
		{
			fieldname: 'from_date',
			fieldtype: 'Date',
			label : __('From Date'),
			default : new Date(date.getFullYear(), date.getMonth(), 1)
 		},
		{
			fieldname : 'to_date',
			fieldtype : 'Date',
			label : __('To Date'),
			default : 'Today',
 		}
	],
};
