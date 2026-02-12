# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from frappe.utils.nestedset import get_root_of
from frappe.desk.treeview import get_all_nodes, get_children
from erpnext.accounts.report.trial_balance_for_party.trial_balance_for_party import execute as _execute

def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)
	if not data:
		frappe.msgprint(_("No Data Found"), alert = True, indicator = "green")

	return columns, data

def get_columns(filters):
	columns = [
		{
			'fieldname' : 'particulars',
			'fieldtype' : 'Data',
			'label' : _('Particulars'),
			'width' : 300,
		},
		{
			'fieldname' : 'customer',
			'fieldtype' : 'Link',
			'label' : _('Customer'),
			'options' : 'Customer',
			'width' : 200
		},
	]

	dates = get_dates_of_year(filters)
	for date in dates:
		columns.append({
			'fieldname' : 'opening_balance_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower()),
			'fieldtype' : 'Data',
			'label' : _('Opening Balance[{0}-{1}]'.format(frappe.utils.getdate(date.get('start')).strftime("%d %B %y"), frappe.utils.getdate(date.get('end')).strftime("%d %B %y"))),
			'width' : 300,
		})	

		columns.append({
			'fieldname' : 'debit_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower()),
			'fieldtype' : 'Data',
			'label' : _('Debit[{0}-{1}]'.format(frappe.utils.getdate(date.get('start')).strftime("%d %B %y"), frappe.utils.getdate(date.get('end')).strftime("%d %B %y"))),
			'width' : 300
		})	

		columns.append({
			'fieldname' : 'credit_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower()),
			'fieldtype' : 'Data',
			'label' : _('Credit[{0}-{1}]'.format(frappe.utils.getdate(date.get('start')).strftime("%d %B %y"), frappe.utils.getdate(date.get('end')).strftime("%d %B %y"))),
			'width' : 300
		})	

		columns.append({
			'fieldname' : 'closing_balance_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower()),
			'fieldtype' : 'Data',
			'label' : _('Closing Balance[{0}-{1}]'.format(frappe.utils.getdate(date.get('start')).strftime("%d %B %y"), frappe.utils.getdate(date.get('end')).strftime("%d %B %y"))),
			'width' : 300
		})	
	return columns

def get_dates_of_year(filters):
	year_start_date = filters.get('from_date')
	year_end_date = filters.get('to_date')
	dates = []
	month_start_date = year_start_date
	month_end_date = frappe.utils.get_last_day(year_start_date)
	dates.append({"start": month_start_date, "end": month_end_date})
	while month_end_date < frappe.utils.getdate(year_end_date):
		next_month_start_date = frappe.utils.add_days(month_end_date, 1)
		next_month_end_date = frappe.utils.get_last_day(next_month_start_date)
		dates.append({"start": next_month_start_date, "end": next_month_end_date})
		month_end_date = next_month_end_date
		
	return dates

def get_ordered_sales_person_tree_data():
	doctype='Sales Person'
	label = 'Sales Team'
	parent = 'Sales Team'
	tree_method = 'frappe.desk.treeview.get_children'
	spt = get_all_nodes(doctype, label, parent, tree_method)

	sorted_sp_parent = spt[0]['parent']
	sorted_sp = []
	out = get_sorted_sp(sorted_sp_parent, spt, sorted_sp)
	sales_persons = assign_levels_to_sales_persons(out)
	return sales_persons

def get_sorted_sp(sorted_sp_parent, spt, sorted_sp):
	for sp in spt:
		if sp['parent'] == sorted_sp_parent:
			if len(sp['data']) > 0:
				for d in sp['data']:
					row = {
							'sales_person' : d['value'],
							'parent' : sp['parent'],
							'is_group' : d['expandable']
						}
					if row not in sorted_sp:
						sorted_sp.append(row)
					sorted_sp_parent = d['value']
					get_sorted_sp(sorted_sp_parent, spt, sorted_sp)
	return sorted_sp

def assign_levels_to_sales_persons(sales_persons):
	root = get_root_of('Sales Person')
	root_nodes = get_children('Sales Person',root)
	root_list = [r['title'] for r in root_nodes]
	sec_level_nodes = []
	for node in root_list:
		sec_root_nodes = get_children('Sales Person',node)
		sec_level_nodes = sec_level_nodes + [r['title'] for r in sec_root_nodes]
	for sp in sales_persons:
		if sp['is_group'] == 1 and sp['parent'] == root:
			sp.update({'level': 0})
		elif sp['is_group'] == 1 and sp['parent'] in root_list:
			sp.update({'level': 1})
		elif sp['is_group'] == 1 and sp['parent'] in sec_level_nodes:
			sp.update({'level': 2})
		elif sp['is_group'] == 1:
			sp.update({'level': 3})
		elif sp['is_group'] == 0:
			if sp['parent'] in root_list:
				sp.update({'level': 1})
			elif sp['parent'] in sec_level_nodes:
				sp.update({'level': 2})
			else:
				sp.update({'level': 4})
	return sales_persons

def get_customer_of_sales_person(sales_persons):
	customers = frappe.db.get_all('Sales Team', {'parenttype':'Customer', 'sales_person':sales_persons}, pluck='parent')
	return customers

def get_customer_wise_details_from_trial_balance_report(data, filters):
	dates = get_dates_of_year(filters)
	if data:
		for d in data:
			if d['type'] == "Customer":
				for date in dates:
					ref_filters = frappe._dict({
						'company': filters.get('company'),
						'fiscal_year' : filters.get('fiscal_year'),
						'from_date' : date.get('start'),
						'to_date' : date.get('end'),
						'party_type' : 'Customer',
						'party' : d['customer']
					})
					report_data = _execute(ref_filters)
					if report_data and len(report_data) > 0:
						detail = report_data[1]
						if detail != []:
							opening_fieldname = 'opening_balance_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
							closing_fieldname = 'closing_balance_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
							debit_fieldname = 'debit_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
							credit_fieldname = 'credit_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
							d.update({
								opening_fieldname : detail[0]['opening_debit'],
								debit_fieldname : detail[0]['debit'],
								credit_fieldname : detail[0]['credit'],
								closing_fieldname : detail[0]['closing_debit']
							})

	return data

def get_total_of_each_sales_persons(output, sales_persons):
	for sp in sales_persons[::-1]:
		total = {}
		for out in output[::-1]:
			if out['parent'] == sp['sales_person']:
				for key, value in out.items():
					if key in ['particulars', 'customer', 'is_group', 'level', 'type', 'parent']:
						continue
					else:
						total[key] = (total[key] if key in total else 0) + out[key]

		for x in output:
			if 'particulars' in x and x['particulars'] == sp['sales_person']:
				for key, value in total.items():
					x[key] = value
					# x[key] = (x[key] if key in x else 0) + value :- If Total Roll Up Not Works Properly Try This
	return output

def get_conditional_data(result, filters):
	response = result
	if filters.get("customer"):
		response = [r for r in result if 'customer' in r and r['customer'] == filters.get("customer")]

	if filters.get("level"):
		response = [r for r in result if 'level' in r and int(r['level']) == int(filters.get("level"))]
		
	return response

def get_conditional_keys(filters):
	dates = get_dates_of_year(filters)
	conditional_keys = []
	for date in dates:
		opening_fieldname = 'opening_balance_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
		closing_fieldname = 'closing_balance_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
		debit_fieldname = 'debit_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
		credit_fieldname = 'credit_{0}'.format(frappe.utils.getdate(date.get('start')).strftime("%B").lower())
		conditional_keys.append(opening_fieldname)
		conditional_keys.append(closing_fieldname)
		conditional_keys.append(debit_fieldname)
		conditional_keys.append(credit_fieldname)

	return conditional_keys

def format_currency_values_in_final_data(result, filters):
	conditional_keys = get_conditional_keys(filters)

	for res in result:
		keys = res.keys()
		if not set(conditional_keys).issubset(set(keys)):
			for key in conditional_keys:
				res[key] = 0

		for key, value in res.items():
			if key in ['particulars', 'customer', 'is_group', 'level', 'type', 'parent']:
				continue
			else:
				res[key] = frappe.format(value if value != None else 0, "Currency")  
				if key.startswith("closing") or key.startswith("opening"):
					res[key] = res[key] + " Dr"

def add_total_row_in_report(result, filters):
	keys = get_conditional_keys(filters)
	total_row = {
		"particulars" : "Total"
	}
	for r in result:
		if 'level' in r and int(r['level']) == 0:
			for key in keys:
				total_row[key] = r[key] + (total_row[key] if key in total_row else 0)
	result.append(total_row)

	return result

def get_data(filters):
	res = []
	sales_persons = get_ordered_sales_person_tree_data()
	
	for sp in sales_persons:
		res.append({
			'particulars': sp['sales_person'],
			'is_group': sp['is_group'],
			'level': sp['level'],
			'type': 'Sales Person',
			'parent': sp['parent']
		})
		
		customers = get_customer_of_sales_person(sp['sales_person'])
		if customers:
			for customer in customers:
				res.append({
					'particulars': customer,
					'customer': customer,
					'parent' : sp['sales_person'],
					'type': 'Customer'
				})
	output = get_customer_wise_details_from_trial_balance_report(res, filters)
	result = get_total_of_each_sales_persons(output, sales_persons)
	if filters:
		result = get_conditional_data(result, filters)
	result = add_total_row_in_report(result, filters)
	format_currency_values_in_final_data(result, filters)
	return result
