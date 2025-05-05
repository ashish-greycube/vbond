// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Sales & Transport Cost Report"] = {
	"filters": [
		{
			'fieldname' : 'from_date',
			'fieldtype' : 'Date',
			'label' : __('From Date'),
		},
		{
			'fieldname' : 'to_date',
			'fieldtype' : 'Date',
			'label' : __('To Date'),
		},
		{
			'fieldname' : 'state',
			'fieldtype' : 'Link',
			'label' : __('State'),
			'options' : 'State VB',
		},
		{
			'fieldname' : 'vehicle_type',
			'fieldtype' : 'Select',
			'label' : __('Vehicle Type'),
			'options' : '\nHired\nDedicated / Company Owned\nTPL(Third Party Logistics)',
		},
		{
			'fieldname' : 'transporter',
			'fieldtype' : 'Link',
			'label' : __('Transporter'),
			'options' : 'Supplier',
			'get_query' : function () {
				return {
					filters : {
						'is_transporter' : 1
					}
				}
			}
		},
	],

	// Formatting Total Row
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if(data.party_name == "TOTAL"){
			value = value.bold()
		}
		return value;
	},
};
