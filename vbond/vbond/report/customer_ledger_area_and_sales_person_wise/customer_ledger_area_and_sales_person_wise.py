# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.treeview import get_all_nodes, get_children
from frappe.utils.nestedset import get_root_of
from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import execute as _execute


def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	msg = get_message()
	return columns, data, msg


def get_columns(filters):
	columns = [
		{
			'fieldname' : 'particulars',
			'fieldtype' : 'Data',
			'label' : _('Particulars'),
			'width' : 380
		},
		{
			'fieldname' : 'opening_balance',
			'fieldtype' : 'Currency',
			'label' : _('Opening Balance'),
			'width' : 160
		},
		{
			'fieldname' : 'invoiced_amount',
			'fieldtype' : 'Currency',
			'label' : _('Invoice Amount'),
			'width' : 160
		},
		{
			'fieldname' : 'paid_amount',
			'fieldtype' : 'Currency',
			'label' : _('Paid Amount'),
			'width' : 160
		},
		{
			'fieldname' : 'credit_note',
			'fieldtype' : 'Currency',
			'label' : _('Credit Note'),
			'width' : 160
		},
		{
			'fieldname' : 'closing_balance',
			'fieldtype' : 'Currency',
			'label' : _('Closing Balance'),
			'width' : 160
		}
	]
	return columns


def get_ordered_sales_person_tree_data():
	doctype='Sales Person'
	label = 'Sales Team'
	parent = 'Sales Team'
	tree_method = 'frappe.desk.treeview.get_children'
	spt = get_all_nodes(doctype, label, parent, tree_method)

	sorted_sp_parent = spt[0]['parent']
	sorted_sp = []
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
	out = get_sorted_sp(sorted_sp_parent, spt, sorted_sp)
	return out


def get_customer_with_sales_persons(sales_persons):
	for sp in sales_persons:
		customer = frappe.db.get_all('Sales Team', {'parenttype':'Customer', 'sales_person':sp['sales_person']}, ['parent'])
		sp.update({
			'customers' : customer
		})

def get_message():
	msg = '''
	<div style="display:flex; gap:5px">
    	<p style="height:20px; width:115px; background-color:red; color:white; padding:0 6px;">For Level 0 Data</p>
		<p style="height:20px; width:110px; background-color:green; color:white; padding:0 6px;">For Level 1 Data</p>
		<p style="height:20px; width:115px; background-color:violet; color:white; padding:0 6px;">For Level 2 Data</p>
		<p style="height:20px; width:115px; background-color:orange; color:white; padding:0 6px;">For Level 3 Data</p>
    </div>
	'''
	return msg

def get_data(filters):
	sales_persons = get_ordered_sales_person_tree_data()
	get_customer_with_sales_persons(sales_persons)
	data = get_report_data(sales_persons, filters)
	
	if filters.get('customer'):
		data = get_filtered_data(data, filters.get('customer'))
	return data

def get_report_data(sales_persons, filters):
	data = []

	cls_data = _execute(filters)
	cls_data = cls_data[1]

	root = get_root_of('Sales Person')
	root_nodes = get_children('Sales Person',root)
	root_list = [r['title'] for r in root_nodes]

	for sp in sales_persons:
		total_opening = total_invoiced = total_paid = total_credit = total_closing = 0
		if sp['is_group'] == 1 and sp['parent'] == "Sales Team":
			level = 0
		elif sp['is_group'] == 1 and sp['parent'] in root_list:
			level = 1
		elif sp['is_group'] == 1:
			level = 2
		else:
			level = 3

		sp_row = {
			'particulars' : sp['sales_person'],
			'level' : level,
			'parent' : sp['parent'],
			'is_group': sp['is_group'],
			'opening_balance' : 0,
			'invoiced_amount' : 0,
			'paid_amount' : 0,
			'credit_note' : 0,
			'closing_balance' : 0
		}
		data.append(sp_row)

		if sp['is_group'] == 1:
			if len(sp['customers']) > 0:
				for customer in sp['customers']:
					for d in cls_data:
						if d['party'] == customer['parent']:
							total_opening = total_opening + d['opening_balance']
							total_invoiced = total_invoiced + d['invoiced_amount']
							total_paid = total_paid + d['paid_amount']
							total_credit = total_credit + d['return_amount']
							total_closing = total_closing + d['closing_balance']

				sp_row.update({
					'opening_balance' : total_opening,
					'invoiced_amount' : total_invoiced,
					'paid_amount' : total_paid,
					'credit_note' : total_credit,
					'closing_balance' : total_closing
				})
		
		elif sp['is_group'] == 0:
			if len(sp['customers']) > 0:
				for customer in sp['customers']:
					customer_row = {
						'particulars' :  customer['parent'],
						'parent': sp['sales_person']
					}
					data.append(customer_row)

					for d in cls_data:
						if d['party'] == customer['parent']:
							customer_row.update({
								'opening_balance' : d['opening_balance'],
								'invoiced_amount' : d['invoiced_amount'],
								'paid_amount' : d['paid_amount'],
								'credit_note' : d['return_amount'],
								'closing_balance' : d['closing_balance'],
							})
							

							total_opening = total_opening + d['opening_balance']
							total_invoiced = total_invoiced + d['invoiced_amount']
							total_paid = total_paid + d['paid_amount']
							total_credit = total_credit + d['return_amount']
							total_closing = total_closing + d['closing_balance']

				sp_row.update({'opening_balance' : total_opening, 'invoiced_amount' : total_invoiced, 'paid_amount' : total_paid, 'credit_note' : total_credit, 'closing_balance' : total_closing })
	
	# Root Node Total Calculation
	for d in data[::-1]:
		if 'is_group' in d and d['is_group'] == 1:
			current_parent = d['particulars']
			grp_opn_total = grp_inv_total = grp_paid_total = grp_rtn_total = grp_cls_total = 0
			for sd in data:
				if sd['parent'] == current_parent:
					grp_opn_total = grp_opn_total + sd['opening_balance']
					grp_inv_total = grp_inv_total + sd['invoiced_amount']
					grp_paid_total = grp_paid_total + sd['paid_amount']
					grp_rtn_total = grp_rtn_total + sd['credit_note']
					grp_cls_total = grp_cls_total + sd['closing_balance']
			
			d.update({
				'opening_balance' : d['opening_balance'] + grp_opn_total,
				'invoiced_amount' : d['invoiced_amount'] + grp_inv_total,
				'paid_amount' : d['paid_amount'] + grp_paid_total,
				'credit_note' : d['credit_note'] + grp_rtn_total,
				'closing_balance' : d['closing_balance'] + grp_cls_total,
			})
	return data
         

def get_filtered_data(data, customer):
	filtereddata = []
	for d in data:
		if d['particulars'] == customer:
			filtereddata.append(d)
	return filtereddata