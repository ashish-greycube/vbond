// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Dedicated Vehicle Loading Sheet"] = {
	"filters": [
		{
			'fieldname' : 'vehicle_number',
			'fieldtype' : 'Link',
			'options' : 'Vehicle',
			'label' : __('Vehicle No'),
			'reqd' : 1
		},
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
	]
};
