// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Revenue vs COGS Report"] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions("Revenue vs COGS Report", 10);

frappe.query_reports["Revenue vs COGS Report"]["filters"].push({
	fieldname: "selected_view",
	label: __("Select View"),
	fieldtype: "Select",
	options: [
		{ value: "Report", label: __("Report View") },
		{ value: "Growth", label: __("Growth View") },
		{ value: "Margin", label: __("Margin View") },
	],
	default: "Report",
	reqd: 1,
});

frappe.query_reports["Revenue vs COGS Report"]["filters"].push({
	fieldname: "accumulated_values",
	label: __("Accumulated Values"),
	fieldtype: "Check",
	default: 1,
});

frappe.query_reports["Revenue vs COGS Report"]["filters"].push({
	fieldname: "include_default_book_entries",
	label: __("Include Default FB Entries"),
	fieldtype: "Check",
	default: 1,
});

frappe.query_reports["Revenue vs COGS Report"]["filters"].push({
	"fieldname": "income_account",
	"label": __("Income Account"),
	"fieldtype": "Link",
	"options": "Account"
});

frappe.query_reports["Revenue vs COGS Report"]["filters"].push({
	"fieldname": "expense_account",
	"label": __("Expense Account"),
	"fieldtype": "Link",
	"options": "Account"
});
