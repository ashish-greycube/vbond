// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Transport Cost"] = {
	"filters": [
		{
			fieldname: 'from_date',
			fieldtype: 'Date',
			label : __('From Date'),
			default : 'Today'
 		},
		{
			fieldname : 'to_date',
			fieldtype : 'Date',
			label : __('To Date'),
			default : 'Today',
 		}
	],
};
