// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Sales vs Collection"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			on_change: function (query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.model.with_doc("Fiscal Year", fiscal_year, function (r) {
					var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
					frappe.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date,
					});
				});
			},
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer"
		},
		{
			fieldname: "level",
			label: __("Up to Level"),
			fieldtype: "Select",
			options: "\n0\n1\n2\n3\n4"
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
		if (data.level == 4) {
			value = `<div style="color:#f57842; font-weight:bold;">${value}</div>`
		}
		if (data.particulars == "Total") {
			value = `<div style="font-weight:bold;">${value}</div>`
		}
		return value;
	},

	onload: function (datatable) {
		$('.layout-main-section').find(".page-form").after(
			`
				<div style="display:flex; gap:5px; padding:10px;">
					<p style="height:20px; width:115px; background-color:red; color:white; padding:0 6px;">For Level 0 Data</p>
					<p style="height:20px; width:110px; background-color:green; color:white; padding:0 6px;">For Level 1 Data</p>
					<p style="height:20px; width:115px; background-color:violet; color:white; padding:0 6px;">For Level 2 Data</p>
					<p style="height:20px; width:115px; background-color:orange; color:white; padding:0 6px;">For Level 3 Data</p>
					<p style="height:20px; width:115px; background-color:#f57842; color:white; padding:0 6px;">For Level 4 Data</p>
				</div>
			`
		);
	}
};
