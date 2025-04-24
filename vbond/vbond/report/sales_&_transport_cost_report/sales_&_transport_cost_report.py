# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
	if not filters: filters = {}

	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	if not data:
		frappe.msgprint("No Data Found")

	return columns, data

def get_columns():
	return [
		{
			'fieldname' : 'date',
			'fieldtype' : 'Date',
			'label' : _('Date'),
			'width' : 120
		},
		{
			'fieldname' : 'party_name',
			'fieldtype' : 'Link',
			'label' : _('Party Name'),
			'options' : 'Customer',
			'width' : 200
		},
		{
			'fieldname' : 'mobile_no',
			'fieldtype' : 'Phone',
			'label' : _('Mobile No'),
			'width' : 130
		},
		{
			'fieldname' : 'invoice_no',
			'fieldtype' : 'Link',
			'label' : _('Invoice No'),
			'options' : 'Sales Invoice',
			'width' : 150
		},
		{
			'fieldname' : 'place',
			'fieldtype' : 'Data',
			'label' : _('Place'),
			'width' : 120
		},
		{
			'fieldname' : 'kms',
			'fieldtype' : 'Float',
			'label' : _('KMs'),
			'width' : 130
		},
		{
			'fieldname' : 'state',
			'fieldtype' : 'Link',
			'label' : _('State'),
			'options' : 'State VB',
			'width' : 80
		},
		{
			'fieldname' : 'tons',
			'fieldtype' : 'Float',
			'label' : _('Tons'),
			'width' : 100
		},
		{
			'fieldname' : 'basic_amount',
			'fieldtype' : 'Currency',
			'label' : _('Basic Amount'),
			'width' : 130
		},
		{
			'fieldname' : 'total_amount',
			'fieldtype' : 'Currency',
			'label' : _('Total Amount'),
			'width' : 130
		},
		{
			'fieldname' : 'transport_amount',
			'fieldtype' : 'Currency',
			'label' : _('Transport Amount'),
			'width' : 130
		},
		{
			'fieldname' : 'transport_cost',
			'fieldtype' : 'Percent',
			'label' : _('Transport Cost'),
			'width' : 130
		},
		{
			'fieldname' : 'vehicle_no',
			'fieldtype' : 'Data',
			'label' : _('Vehicle No'),
			'width' : 150
		},
		{
			'fieldname' : 'transport_name',
			'fieldtype' : 'Data',
			'label' : _('Transport Name'),
			'width' : 150
		},
		{
			'fieldname' : 'dispatch_date',
			'fieldtype' : 'Date',
			'label' : _('Dispatch Date'),
			'width' : 130
		},
	]

def get_conditions(filters):
	condition = ""
	curr_month = datetime.now().strftime('%m')
	curr_year = datetime.now().strftime('%Y')

	if not filters.get('si_date'):
		condition += f"tsi.posting_date BETWEEN '{curr_year}-{curr_month}-01' AND '{curr_year}-{curr_month}-31'"
	
	if filters.get('si_date'):
		if filters.get('si_date') >= f'{curr_year}-{curr_month}-01' and  filters.get('si_date') <= f'{curr_year}-{curr_month}-31':
			condition += f"tsi.posting_date BETWEEN '{curr_year}-{curr_month}-01' AND '{curr_year}-{curr_month}-31' and tsi.posting_date = '{filters.get('si_date')}'"
		else:
			condition += f"tsi.posting_date = '{filters.get('si_date')}'"

	if filters.get('customer'):
		condition += f"and tsi.customer = '{filters.get('customer')}'"	

	if filters.get('state'): 
		condition += f"and tsi.custom_state = '{filters.get('state')}'"	

	if filters.get('vehicle_type'):
		condition += f"and tsi.custom_vehicle_type = '{filters.get('vehicle_type')}'"

	return condition

def get_data(filters):
	total_kms = 0
	total_tons = 0
	total_amount = 0
	total_basic_amount = 0
	total_transport_amount = 0
	total_transport_percent = 0

	conditions = get_conditions(filters)
	data = []

	invoices = frappe.db.sql(
		f'''
		SELECT 
			tsi.posting_date as 'date',
			tsi.customer as 'partyName',
			tsi.contact_person as 'mobileNo',
			tsi.name as 'invoiceNo',
			tsi.custom_transport_destination as 'place',
			tsi.custom_destination_distance as 'kms',
			tsi.custom_state as 'state',
			tsi.total_net_weight as 'weight',
			tsi.custom_basic_amount as 'basicAmount',
			tsi.rounded_total as 'totalAmount',
			tsi.custom_transport_cost as 'transportAmount',
			tsi.custom_vehicle_number as 'dedicatedNo',
			tsi.vehicle_no as 'hiredNo',
			tsi.transporter as 'transporterName',
			tsi.custom_vehicle_type as 'type'
		FROM 
			`tabSales Invoice` tsi 
		WHERE 
			{conditions}
		ORDER BY
			tsi.posting_date;
		''',
	as_dict = 1, debug = 1)

	if len(invoices) > 0:
		for invoice in invoices:
			# Total Weight In Tons
			kg_weight = invoice.weight
			tons_weight = kg_weight / 1000

			# Trasport Percent 
			transport_percent = 0
			if invoice.basicAmount and invoice.transportAmount > 0:
				transport_percent = (invoice.transportAmount / invoice.basicAmount) * 100

			# Dispatch Date 
			delivery_note = frappe.db.get_value('Sales Invoice Item', {'parent' : invoice.invoiceNo}, ['delivery_note'])
			delivery_date = frappe.db.get_value('Delivery Note', {'name' : delivery_note}, ['posting_date'])

			row = frappe._dict({
				'date' : invoice.date,
				'party_name' : invoice.partyName,
				'mobile_no' : frappe.db.get_value('Contact', {'name' : invoice.mobileNo}, ['mobile_no']),
				'invoice_no' : invoice.invoiceNo,
				'place' : invoice.place,
				'kms' : invoice.kms,
				'state' : invoice.state,
				'tons' : tons_weight,
				'basic_amount' : invoice.basicAmount,
				'total_amount' : invoice.totalAmount,
				'transport_amount' : invoice.transportAmount,
				'transport_cost' : transport_percent,
				'vehicle_no' : invoice.dedicatedNo if invoice.type == 'Dedicated / Company Owned' else invoice.hiredNo,
				'transport_name' : 'Company Vehicle' if invoice.type == 'Dedicated / Company Owned' else invoice.transporterName,
				'dispatch_date' : delivery_date
			})
			data.append(row)

			# Total rows
			total_kms = total_kms + invoice.kms
			total_tons = total_tons + tons_weight
			total_basic_amount = total_basic_amount + invoice.basicAmount
			total_amount = total_amount + invoice.totalAmount
			total_transport_amount = total_transport_amount + invoice.transportAmount

	if total_basic_amount > 0:
		total_transport_percent = total_transport_percent + ((total_transport_amount / total_basic_amount) * 100)
	else:
		total_transport_percent = total_transport_percent + 0

	total_row = frappe._dict({
		'party_name' : 'TOTAL',
		'kms' : None,
		'tons' : total_tons,
		'basic_amount' : total_basic_amount,
		'total_amount' : total_amount,
		'transport_amount' : total_transport_amount,
		'transport_cost' : total_transport_percent
	})

	data.append(total_row)
	return data