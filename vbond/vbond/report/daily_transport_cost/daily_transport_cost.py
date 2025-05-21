# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, add_to_date, today

def execute(filters=None):
	if not filters: filters = {}

	columns, data = [], []
	
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
		{
			"fieldname" : "date",
			"fieldtype" : "Date",
			"label" : _("Date"),
			"width" : 120
		},
		{
			"fieldname" : "no_of_vehicles",
			"fieldtype" : "Float",
			"label" : _("No of Vehicles"),
			"width" : 130
		},
		{
			"fieldname" : "invoice_value",
			"fieldtype" : "Currency",
			"label" : _("Invoice Value"),
			"width" : 130
		},
		{
			"fieldname" : "disp_tonnage",
			"fieldtype" : "Float",
			"label" : _("Disp Tonnage"),
			"width" : 130
		},
		{
			"fieldname" : "transport_cost",
			"fieldtype" : "Currency",
			"label" : _("Transport Cost"),
			"width" : 130
		},
		{
			"fieldname" : "cost_percentage",
			"fieldtype" : "Percent",
			"label" : _("Cost(%)"),
			"width" : 130,
			'precision' : 2
		}
	]

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)
	no_of_days = date_diff(conditions.get('to_date'), conditions.get('from_date'))

	total_vehicles = 0
	total_invoice_value = 0
	total_disp_tonnage = 0
	total_transport_cost =0 
	total_cost_percentage = 0
	
	for i in range(0, no_of_days+1):
		if conditions.get('to_date') == conditions.get('from_date'):
			curr_date = conditions.get('from_date')
		else:
			curr_date = add_to_date(conditions.get('to_date'), days = -i)

		if curr_date >= conditions.get('from_date'):
			invoice_data = frappe.db.sql(f"""
								SELECT 
									COUNT(DISTINCT(tsi.vehicle_no)) AS 'totalVehicles', 
									SUM(tsi.total) AS 'totalInvoiceValue', 
									SUM(tsi.total_net_weight) AS 'totalNetWeight', 
									SUM(tsi.custom_transport_cost) AS 'totalTransportCost'
								FROM 
									`tabSales Invoice` tsi 
								WHERE 
									posting_date = '{curr_date}'; 
								""",as_dict = 1)
		
			if invoice_data[0]['totalInvoiceValue'] == None:
				invoice_data[0]['totalInvoiceValue'] = 0.0

			if invoice_data[0]['totalNetWeight'] == None:
				invoice_data[0]['totalNetWeight'] = 0.0

			if invoice_data[0]['totalTransportCost'] == None:
				invoice_data[0]['totalTransportCost'] = 0.0

			cost_percentage = 0
			if invoice_data[0]['totalInvoiceValue']  > 0:
				cost_percentage = (invoice_data[0]['totalTransportCost'] / invoice_data[0]['totalInvoiceValue']) * 100

			row_data = frappe._dict({
				'date' : curr_date,
				'no_of_vehicles' : invoice_data[0]['totalVehicles'],
				'invoice_value' : invoice_data[0]['totalInvoiceValue'] ,
				'disp_tonnage' : invoice_data[0]['totalNetWeight'] / 1000 ,
				'transport_cost' : invoice_data[0]['totalTransportCost'] ,
				'cost_percentage' : cost_percentage
			})
			data.append(row_data)

			# Total Row Calculation
			total_vehicles = total_vehicles + invoice_data[0]['totalVehicles']
			total_invoice_value = total_invoice_value + invoice_data[0]['totalInvoiceValue'] 
			total_disp_tonnage = total_disp_tonnage + (invoice_data[0]['totalNetWeight'] / 1000)
			total_transport_cost = total_transport_cost + invoice_data[0]['totalTransportCost']
	
	if total_invoice_value > 0:
		total_cost_percentage = (total_transport_cost / total_invoice_value) * 100

	totol_row = frappe._dict({
		'no_of_vehicles' : total_vehicles,
		'invoice_value' : total_invoice_value ,
		'disp_tonnage' : total_disp_tonnage,
		'transport_cost' : total_transport_cost,
		'cost_percentage' : total_cost_percentage
	})

	data.insert(0, totol_row)
	return data[::-1]