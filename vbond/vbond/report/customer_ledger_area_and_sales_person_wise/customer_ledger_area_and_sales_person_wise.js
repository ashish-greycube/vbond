// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Ledger Area and Sales Person Wise"] = {
	"filters": [
		{
			'fieldname': 'company',
			'fieldtype': 'Link',
			'label': __('Company'),
			'default': frappe.defaults.get_user_default("Company"),
			'options' : 'Company'
		},
		{
			'fieldname': 'from_date',
			'fieldtype': 'Date',
			'label': 'From Date',
			'default': frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			'reqd' : 1,
		},
		{
			'fieldname': 'to_date',
			'fieldtype': 'Date',
			'label': 'TO Date',
			'default': frappe.datetime.get_today(),
			'reqd' : 1,
		},
		{
			'fieldname': 'customer',
			'fieldtype': 'Link',
			'label': 'Customer',
			'options': 'Customer',
		},
	],

	formatter: function (value, row, column, data, default_formatter, filter) {
		value = default_formatter(value, row, column, data);
		if (data.level == 0) {
			value = `<div style="color:red; font-weight:bold;">${value}</div>`
		}
		if (data.level == 1) {
			value = `<div style="color:green; font-weight:bold;">${value}</div>`
		}
		if (data.level == 2) {
			value = `<div style="color:violet; font-weight:bold;">${value}</div>`
		}
		if (data.level == 3) {
			value = `<div style="color:orange; font-weight:bold;">${value}</div>`
		}
		return value;
	},

};
