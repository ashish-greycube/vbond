// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Ageing Report"] = {
	"filters": [
		{
			'fieldname': 'company',
			'fieldtype': 'Link',
			'label': 'Company',
			'options': 'Company',
			'default': 'Value Pack India Private Limited'
		},
		{
			'fieldname': 'range',
			'fieldtype': 'Data',
			'label': 'Range',
			'default': '30, 45, 60, 90, 120, 150, 180'
		},
		{
			'fieldname': 'posting_date',
			'fieldtype': 'Date',
			'label': 'Posting Date',
			'default': 'Today'
		},
		{
			'fieldname': 'upto_level',
			'fieldtype': 'Select',
			'label': 'Up To',
			'options': '\n0\n1\n2\n3\n4'
		}
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
		if (data.level == 4) {
			value = `<div style="color:#f57842; font-weight:bold;">${value}</div>`
		}
		if (data.particulars == 'Total') {
			value = value.bold()
		}
		return value;
	},
};
