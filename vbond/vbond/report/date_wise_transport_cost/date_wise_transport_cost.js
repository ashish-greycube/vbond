// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Date Wise Transport Cost"] = {
	"filters": [
		{
			fieldname: 'date',
			fieldtype: 'Date',
			label : __('Date'),
			default : 'Today'		
		}
	]
};
