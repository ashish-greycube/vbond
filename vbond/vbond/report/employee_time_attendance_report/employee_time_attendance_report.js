// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

var date  = new Date()
frappe.query_reports["Employee Time Attendance Report"] = {
	"filters": [
		{
			fieldname : 'from_date',
			fieldtype : 'Date',
			label : __('From Date'),
			default : new Date(date.getFullYear(), date.getMonth(), 1)
		},
		{
			fieldname : 'to_date',
			fieldtype : 'Date',
			label : __('To Date'),
			default : frappe.datetime.get_today()
		},
		{
			fieldname : 'employee',
			fieldtype : 'Link',
			label : __('Employee'),
			options : 'Employee'
		},
		{
			fieldname : 'shift',
			fieldtype : 'Link',
			label : __('Shift'),
			options : 'Shift Type'
		},
		{
			fieldname : 'department',
			fieldtype : 'Link',
			label : __('Department'),
			options : 'Department'
		},
	],

	formatter: function (value, row, column, data, default_formatter, filter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "employee") {
			value = value.bold()
		}
		return value;
	},
};
