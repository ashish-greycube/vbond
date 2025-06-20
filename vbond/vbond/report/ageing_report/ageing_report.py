# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today
from erpnext import get_default_company
from frappe.desk.treeview import get_all_nodes
from frappe.utils.nestedset import get_descendants_of
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import execute as ars_execute

def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	msg = '''
	<div style="display:flex; gap:5px">
    	<p style="height:20px; width:110px; background-color:red; color:white; padding:0 5px;">For Level 1 Data</p>
		<p style="height:20px; width:110px; background-color:green; color:white; padding:0 5px;">For Level 2 Data</p>
		<p style="height:20px; width:145px; background-color:blue; color:white; padding:0 6px;">For Level 3 & 3.1 Data</p>
		<p style="height:20px; width:135px; background-color:orange; color:white; padding:0 9px;">For Level 3.1.1 Data</p>
    </div>
	'''
	return columns, data, msg 

def get_columns():
	columns = [
		{
			'fieldname': 'particulars',
			'fieldtype': 'Data',
			'label': _('Particulars'),
			'width': 400
		},
		{
			'fieldname': 'customer',
			'fieldtype': 'Link',
			'label': _('Customer'),
			'options' : 'Customer',
			'width': 200
		},
		{
			'fieldname': 'pending_bills',
			'fieldtype': 'Float',
			'label': _('Pending Bills'),
			'width': 130
		},
		{
			'fieldname': 'range1',
			'fieldtype': 'Float',
			'label': _('(< 30 Days)'),
			'width': 130
		},
		{
			'fieldname': 'range2',
			'fieldtype': 'Float',
			'label': _('30 to 45 Days'),
			'width': 130
		},
		{
			'fieldname': 'range3',
			'fieldtype': 'Float',
			'label': _('45 to 60 Days'),
			'width': 130
		},
		{
			'fieldname': 'range4',
			'fieldtype': 'Float',
			'label': _('60 to 90 Days'),
			'width': 130
		},
		{
			'fieldname': 'range5',
			'fieldtype': 'Float',
			'label': _('90 to 120 Days'),
			'width': 130
		},
		{
			'fieldname': 'range6',
			'fieldtype': 'Float',
			'label': _('120 to 150 Days'),
			'width': 130
		},
		{
			'fieldname': 'range7',
			'fieldtype': 'Float',
			'label': _('150 to 180 Days'),
			'width': 130
		},
		{
			'fieldname': 'range8',
			'fieldtype': 'Float',
			'label': _('(> 180 Days)'),
			'width': 130
		}
	]
	return columns

def get_conditions(filters):
	conditions = {}
	for key,value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)

	# Accounts Receivable Summary Report Data
	ars_filters = {
		'company': filters.get('company') or get_default_company(),
		'ageing_based_on': 'Posting Date',
		'report_date' : filters.get('posting_date') or today(),
		'range' : filters.get('range') or '30, 45, 60, 90, 120, 150, 180'
	}
	ars_data = ars_execute(ars_filters)	
	ars_data = ars_data[1]
	
	# Getting Sales Person Tree View Data And Converting Into List
	
	doctype='Sales Person'
	label = 'Sales Team'
	parent = 'Sales Team'
	tree_method = 'frappe.desk.treeview.get_children'
	spt = get_all_nodes(doctype, label, parent, tree_method)

	sales_person_list = []
	for sp in spt:
		parent = sp['parent']
		if len(sp['data']) > 0:
			for d in sp['data']:
				sales_person_list.append({
					"parent": parent,
					"value": d['value'],
					"expandable": d['expandable'],
					"total" : 0
				})
	
	# Converting Customer Data With Sales Persons
	for d in ars_data:
		sales_person = frappe.db.sql(
			f"SELECT sales_person as sp FROM `tabSales Team` WHERE parenttype = 'Customer' AND parent = '{d['party']}';", as_dict=True
		)
		d['sales_person'] = sales_person[0]['sp'] if sales_person != [] else None
	
	# Final Output Calculation
	final_output = []

	# Modifying Sales Person Tree View List Data For Proper Formatting
	for i in range(1, len(sales_person_list)):
		if sales_person_list[i]['parent'] == 'Sales Team' and (sales_person_list[i]['expandable'] == 0 or sales_person_list[i]['expandable'] == 1):
			element = sales_person_list.pop(i)
			sales_person_list.append(element)
	
	for sp in sales_person_list:
		total_outstanding = 0
		r1total = r2total = r3total = r4total = r5total = r6total = r7total = r8total = 0

		# Calculating Level 1 Data
		# If element is group node than only create its row
		if sp['parent'] == 'Sales Team' and sp['expandable'] == 1:
			new_fr = { 'particulars' : sp['value'], 'level' : 0,}
			if new_fr not in final_output:
				final_output.append(new_fr)


		# If not group node then create its row and find its customers
		elif sp['parent'] == 'Sales Team' and sp['expandable'] == 0:
			new_fr = { 'particulars' : sp['value'], 'level' : 0,}
			if new_fr not in final_output:
				final_output.append(new_fr)

			for data in ars_data:
				if data['sales_person'] == sp['value']:
					new_fr = { 'particulars' : data['party']}
					if new_fr not in final_output:
						final_output.append(new_fr)
						total_outstanding = total_outstanding + data['outstanding']
						r1total = r1total + data['range1'] if 'range1' in  data else 0
						r2total = r2total + data['range2'] if 'range2' in  data else 0
						r3total = r3total + data['range3'] if 'range3' in  data else 0
						r4total = r4total + data['range4'] if 'range4' in  data else 0
						r5total = r5total + data['range5'] if 'range5' in  data else 0
						r6total = r6total + data['range6'] if 'range6' in  data else 0
						r7total = r7total + data['range7'] if 'range7' in  data else 0
						r8total = r8total + data['range8'] if 'range8' in  data else 0
			for fr in final_output:
				if fr['particulars'] == sp['value']:
					fr['pending_bills'] = total_outstanding
					fr['range1'] =  r1total 
					fr['range2'] = 	r2total 
					fr['range3'] = 	r3total 
					fr['range4'] =  r4total 
					fr['range5'] = 	r5total 
					fr['range6'] = 	r6total 
					fr['range7'] = 	r7total 
					fr['range8'] = 	r8total 

		# Calculating Level 2 Data
		# Adding level2 data and its child nodes with sales persons
		else:
			if sp['parent'] == "National Head  Sales and Marketing":
				doctype = 'Sales Person'
				name = sp['value']
				order_by = 'rgt desc'
				childs = get_descendants_of(doctype, name,order_by)
				new_fr = { 'particulars' : sp['value'], 'level' : 1 }
				if new_fr not in final_output: 
					final_output.append(new_fr) 

				amnts = []
				amnts.append({ 'parent' : sp['parent'], 'title':sp['value'], 'amount':0, 'r1t' : 0, 'r2t':0, 'r3t':0,'r4t': 0, 'r5t':0, 'r6t':0, 'r7t':0, 'r8t': 0, })
				for child in childs:
					totals = 0
					range1total = range2total = range3total = range4total = range5total = range6total = range7total = range8total = 0
					for sps in sales_person_list:
						if sps['value'] == child and sps['expandable'] == 1:
							new_fr = { 'particulars' : child, 'level' : 2 }
							if new_fr not in final_output: 
								final_output.append(new_fr) 
							for data in ars_data:
								if data['sales_person'] == child:
										totals = totals + data['outstanding']
										range1total = range1total + data['range1'] if 'range1' in  data else 0
										range2total = range2total + data['range2'] if 'range2' in  data else 0
										range3total = range3total + data['range3'] if 'range3' in  data else 0
										range4total = range4total + data['range4'] if 'range4' in  data else 0
										range5total = range5total + data['range5'] if 'range5' in  data else 0
										range6total = range6total + data['range6'] if 'range6' in  data else 0
										range7total = range7total + data['range7'] if 'range7' in  data else 0 
										range8total = range8total + data['range8'] if 'range8' in  data else 0
							amnts.append({ 'parent' : sps['parent'], 'title':child, 'amount':totals, 'r1t' : range1total, 'r2t':range2total, 'r3t':range3total,'r4t': range4total, 'r5t':range5total, 'r6t':range6total, 'r7t':range7total, 'r8t': range8total })

						elif sps['value'] == child and sps['expandable'] == 0:
							new_fr = { 'particulars' : child, 'level' : 3 }
							if new_fr not in final_output: 
								final_output.append(new_fr) 
							for data in ars_data:
								if data['sales_person'] == child:
									new_fr = { 'particulars' : data['party'], 'customer' : data['party'], 'parent' : child}
									if new_fr not in final_output:
										final_output.append(new_fr)
										totals = totals + data['outstanding']
										range1total = range1total + data['range1'] if 'range1' in  data else 0
										range2total = range2total + data['range2'] if 'range2' in  data else 0
										range3total = range3total + data['range3'] if 'range3' in  data else 0
										range4total = range4total + data['range4'] if 'range4' in  data else 0
										range5total = range5total + data['range5'] if 'range5' in  data else 0
										range6total = range6total + data['range6'] if 'range6' in  data else 0
										range7total = range7total + data['range7'] if 'range7' in  data else 0
										range8total = range8total + data['range8'] if 'range8' in  data else 0
							amnts.append({ 'parent' : sps['parent'], 'title':child, 'amount':totals, 'r1t' : range1total, 'r2t':range2total, 'r3t':range3total,'r4t': range4total, 'r5t':range5total, 'r6t':range6total, 'r7t':range7total, 'r8t': range8total })
			
				# roll up calculation of total values
				unique_total = []
				unique_parents = []

				# Unique Level 2 Data Total
				for amnt in amnts:
					parent = amnt['parent']
					if parent not in unique_parents:
						unique_parents.append(parent)

				unique_parents = unique_parents[::-1]
				
				for up in unique_parents:
					cur_amt_total = 0
					cur_r1t = cur_r2t = cur_r3t = cur_r4t = cur_r5t = cur_r6t = cur_r7t = cur_r8t = 0
					for amnt in amnts:
						if amnt['parent'] == up:
							cur_amt_total = cur_amt_total + amnt['amount']
							cur_r1t = cur_r1t + amnt['r1t']
							cur_r2t = cur_r2t + amnt['r2t']
							cur_r3t = cur_r3t + amnt['r3t']
							cur_r4t = cur_r4t + amnt['r4t']
							cur_r5t = cur_r5t + amnt['r5t']
							cur_r6t = cur_r6t + amnt['r6t']
							cur_r7t = cur_r7t + amnt['r7t']
							cur_r8t = cur_r8t + amnt['r8t']
					for amnt in amnts:
						if amnt['title'] == up:
							# print(amnt)
							amnt['amount'] = amnt['amount'] + cur_amt_total
							amnt['r1t'] = amnt['r1t'] + cur_r1t
							amnt['r2t'] = amnt['r2t'] + cur_r2t
							amnt['r3t'] = amnt['r3t'] + cur_r3t
							amnt['r4t'] = amnt['r4t'] + cur_r4t
							amnt['r5t'] = amnt['r5t'] + cur_r5t
							amnt['r6t'] = amnt['r6t'] + cur_r6t
							amnt['r7t'] = amnt['r7t'] + cur_r7t
							amnt['r8t'] = amnt['r8t'] + cur_r8t
							unique_total.append({'title': up, 'total': amnt['amount'] or cur_amt_total, 'range1' : amnt['r1t'], 'range2':amnt['r2t'], 'range3':amnt['r3t'], 'range4':amnt['r4t'], 'range5':amnt['r5t'], 'range6':amnt['r6t'], 'range7':amnt['r7t'], 'range8':amnt['r8t']})
				
				for amnt in amnts:
					title = amnt['title']
					isExist = False
					for ut in unique_total:
						if ut['title'] == title:
							isExist = True
					if isExist == False:
						unique_total.append({'title': title, 'total': amnt['amount'], 'range1' : amnt['r1t'], 'range2':amnt['r2t'], 'range3':amnt['r3t'], 'range4':amnt['r4t'], 'range5':amnt['r5t'], 'range6':amnt['r6t'], 'range7':amnt['r7t'], 'range8':amnt['r8t']})
				
				
				# Each Sales Persons Total Calculation
				for fr in final_output:
					for ut in unique_total:
						if fr['particulars'] == ut['title']:
							fr['pending_bills'] = ut['total']
							fr['range1'] = ut['range1']
							fr['range2'] = ut['range2']
							fr['range3'] = ut['range3']
							fr['range4'] = ut['range4']
							fr['range5'] = ut['range5']
							fr['range6'] = ut['range6']
							fr['range7'] = ut['range7']
							fr['range8'] = ut['range8']
				
				houtstanding = hr1t = hr2t = hr3t = hr4t = hr5t = hr6t = hr7t = hr8t = 0
				for fr in final_output:
					if 'level' in fr and fr['level'] == 1:
						houtstanding = houtstanding + fr['pending_bills']
						hr1t = hr1t + fr['range1']
						hr2t = hr2t + fr['range2']
						hr3t = hr3t + fr['range3']
						hr4t = hr4t + fr['range4']
						hr5t = hr5t + fr['range5']
						hr6t = hr6t + fr['range6']
						hr7t = hr7t + fr['range7']
						hr8t = hr8t + fr['range8']

				for fr in final_output:		
					if fr['particulars'] == 'National Head  Sales and Marketing' and fr['level'] == 0:
						fr.update({
							'pending_bills' : houtstanding,
							'range1' : hr1t,
							'range2' : hr2t,
							'range3' : hr3t,
							'range4' : hr4t,
							'range5' : hr5t,
							'range6' : hr6t,
							'range7' : hr7t,
							'range8' : hr8t
						})

		


	for fr in final_output:
		for data in ars_data:
			if fr['particulars'] == data['party']:
				if not 'pending_bills' in fr:
					fr['pending_bills'] = data['outstanding'] 
				fr['range1'] = data['range1'] if 'range1' in  data else 0
				fr['range2'] = data['range2'] if 'range2' in  data else 0
				fr['range3'] = data['range3'] if 'range3' in  data else 0
				fr['range4'] = data['range4'] if 'range4' in  data else 0
				fr['range5'] = data['range5'] if 'range5' in  data else 0
				fr['range6'] = data['range6'] if 'range6' in  data else 0
				fr['range7'] = data['range7'] if 'range7' in  data else 0
				fr['range8'] = data['range8'] if 'range8' in  data else 0
	
	
	sorted_sp_parent = spt[0]['parent']
	sorted_sp = []
	def get_sorted_sp(sorted_sp_parent, spt, sorted_sp):
		for sp in spt:
			if sp['parent'] == sorted_sp_parent:
				if len(sp['data']) > 0:
					for d in sp['data']:
						sorted_sp.append(d['value'])
						sorted_sp_parent = d['value']
						get_sorted_sp(sorted_sp_parent, spt, sorted_sp)
		return sorted_sp
	out = get_sorted_sp(sorted_sp_parent, spt, sorted_sp)

	def check_is_present_or_not(output_report_data, fr, o):
		isPresent = False
		for output in output_report_data:
			if 'parent' in output:
				if output['parent'] == o and output['particulars'] == fr['particulars']:
					isPresent = True
					break
		return isPresent

	def check_particulars(output_report_data, fr, o):
		isAvailable = False
		for output in output_report_data:
			if output['particulars'] == fr['particulars']:
				isAvailable = True
				break
		return isAvailable

	output_report_data = []
	for o in out:
		for fr in final_output:
			if fr['particulars'] == o:
				r = check_particulars(output_report_data, fr, o)
				if r == False:
					output_report_data.append(fr)

			elif 'parent' in fr:
				if fr['parent'] == o:
					res = check_is_present_or_not(output_report_data, fr, o)

					if res == False:
						output_report_data.append(fr)

	return output_report_data	