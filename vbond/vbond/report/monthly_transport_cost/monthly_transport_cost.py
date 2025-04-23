# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	if filters.get('from_date') > filters.get('to_date'):
		frappe.msgprint("From Date Should Be Less Than To Date.")

	columns, data = [], []
	columns = get_columns()
	data = get_data(filters, columns)

	if not data:
		frappe.msgprint("No Data Found")

	return columns, data

def get_columns():
	# States For Dynamically Column Creation 
	states = frappe.db.get_list('State VB', fields = ['state'])  

	columns =  [{
		'fieldname' : 'details',
		'fieldtype' : 'Data',
		'label' : _('Details'),
		'width': 150
	}]

	for s in states:
		columns.append({
			'fieldname' : (s.state).lower(),
			'fieldtype' : 'Float',
			'label' : _(s.state),
			'width': 140,
		})
	
	columns.append({
		'fieldname' : 'total_mtd',
		'fieldtype' : 'Float',
		'label' : _('Total MTD'),
		'width': 140
	})
	return columns

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions

def get_data(filters, columns):
	conditions = get_conditions(filters)
	details = ['Vehicles', 'Vehicle Usages(%)', 'Invoice Value', 'Tonnage', 'TP Cost', 'TP Cost(%)', 'Cost Per Ton']
	data = []

	invoices = frappe.db.sql("""
					SELECT 
						tsi.custom_state,
						COUNT(DISTINCT(tsi.custom_vehicle_number)) + COUNT(DISTINCT(tsi.vehicle_no)) AS 'totalVehicles', 
						SUM(tsi.total) AS 'totalInvoiceValue', 
						SUM(tsi.total_net_weight) AS 'totalNetWeight', 
						SUM(tsi.custom_transport_cost) AS 'totalTransoprtCost'
					FROM 
						`tabSales Invoice` tsi 
					WHERE 
						posting_date BETWEEN '{0}' AND '{1}'
					GROUP BY tsi.custom_state; 
				""".format(conditions.get('from_date'), conditions.get('to_date'))
				, as_dict = 1)
	
	if len(invoices) > 0:
		total_vehicles = 0
		for invoice in invoices:
			total_vehicles = total_vehicles + invoice.get('totalVehicles')

		# Looping details to create rows of details
		for i in range(len(details)):   								
			row_list = []
			total_mtd = 0

			# Looping columns to fill data in each rows
			for column in columns:	

				# Checking for details column 
				if column.get('fieldname') == 'details':				
					col_data = (column.get('fieldname'), details[i])	
					row_list.append(col_data)
				
				total_invoice_amounts = 0
				total_transport_amounts = 0
				total_tonnage = 0

				# Traversing each invoice in data to fill values
				for invoice in invoices:								
					total_invoice_amounts = total_invoice_amounts + invoice.get('totalInvoiceValue')
					total_transport_amounts = total_transport_amounts + invoice.get('totalTransoprtCost')
				
					total_tonnage = total_tonnage + invoice.get('totalNetWeight') / 1000
					total_tp_cost_percent = (total_transport_amounts / total_invoice_amounts) * 100
					if invoice.get('totalVehicles') > 0:
						curr_state_vehicle_percent = (invoice.get('totalVehicles') / total_vehicles) * 100
					else: curr_state_vehicle_percent = 0
					
					# Filling values to the columns
					if invoice.get('custom_state') != None and invoice.get('custom_state').lower() == column.get('fieldname'):
						if details[i] == 'Vehicles':
							col_data = (column.get('fieldname'), invoice.get('totalVehicles'))
							total_mtd = total_mtd + invoice.get('totalVehicles')

						elif details[i] == 'Vehicle Usages(%)':		
							col_data = (column.get('fieldname'), curr_state_vehicle_percent)
							total_mtd = total_mtd + curr_state_vehicle_percent
							
						elif details[i] == 'Invoice Value':
							col_data = (column.get('fieldname'), invoice.get('totalInvoiceValue'))
							total_mtd = total_mtd + invoice.get('totalInvoiceValue')

						elif details[i] == 'Tonnage':
							tonnage_value = invoice.get('totalNetWeight') / 1000
							col_data = (column.get('fieldname'), tonnage_value)
							total_mtd = total_mtd + tonnage_value 

						elif details[i] == 'TP Cost':
							col_data = (column.get('fieldname'), invoice.get('totalTransoprtCost'))
							total_mtd = total_mtd + invoice.get('totalTransoprtCost')

						elif details[i] == 'TP Cost(%)':
							tp_cost = invoice.get('totalTransoprtCost') / invoice.get('totalInvoiceValue') * 100
							col_data = (column.get('fieldname'), round(tp_cost, 2))
							
						elif details[i] == 'Cost Per Ton':
							if  invoice.get('totalNetWeight') / 1000 > 0:
								per_ton_cost = invoice.get('totalTransoprtCost') / (invoice.get('totalNetWeight') / 1000)
							else: 
								per_ton_cost = 0
							col_data = (column.get('fieldname'),round(per_ton_cost, 2))

						row_list.append(col_data)
						
				# Calculating totalMTD values 
				if column.get('fieldname') == 'total_mtd':
					if details[i] == 'TP Cost(%)':
						col_data = (column.get('fieldname'), total_tp_cost_percent)
					elif details[i] == 'Cost Per Ton':
						total_cpt = total_transport_amounts / total_tonnage
						col_data = (column.get('fieldname'), total_cpt)
					else:
						col_data = (column.get('fieldname'), total_mtd)
					
					row_list.append(col_data)
			
			# Making a dict of row and appending to the data list
			row = {}
			row.update(row_list)
			data.append(row)

	return data