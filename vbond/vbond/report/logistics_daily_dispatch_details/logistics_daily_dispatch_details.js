// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Logistics Daily Dispatch Details"] = {
	"filters": [
		{
			'fieldname' : 'from_date',
			'fieldtype' : 'Date',
			'label' : __('From Date'),
			'default' : frappe.datetime.month_start()
		},
		{
			'fieldname' : 'to_date',
			'fieldtype' : 'Date',
			'label' : __('To Date'),
			'default' : frappe.datetime.get_today()
		}
	],

	formatter: function(value, row, column, data, default_formatter){
		value = default_formatter(value, row, column, data);
		if (data.party_name == "TOTAL") {
			value = value.bold()
		}
		return value;
	}
};
