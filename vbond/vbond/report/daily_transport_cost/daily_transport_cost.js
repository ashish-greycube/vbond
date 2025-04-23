// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

var date  = new Date()
frappe.query_reports["Daily Transport Cost"] = {
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
			on_change: function() {
				date = new Date(frappe.query_report.get_filter_value("to_date"));
				newDate = new Date(date.getFullYear(), date.getMonth(), 1)
				frappe.query_report.set_filter_value("from_date", newDate);
				frappe.query_report.refresh()
			}
 		}
	], 

	formatter: function(value, row, column, data, default_formatter){
		value = default_formatter(value, row, column, data);
		if (data.date == null) {
			value = value.bold()
		}
		return value;
	}
};
