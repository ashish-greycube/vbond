# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns, data = [], []
	
	columns = get_columns()
	data = get_data(filters)

	if not data:
		frappe.msgprint('No Data Found')

	return columns, data

def get_columns():
	return [
		{
			'fieldname' : 'so_creation_date',
			'fieldtype' : 'Date',
			'label' : _('Date'),
			'width' : 120
		},
		{
			'fieldname' : 'so_number',
			'fieldtype' : 'Link',
			'label' : _('SO No'),
			'options' : 'Sales Order',
			'width' : 180
		},
		{
			'fieldname' : 'so_transaction_date',
			'fieldtype' : 'Date',
			'label' : _('SO Date'),
			'width' : 120
		},
		{
			'fieldname' : 'party_name',
			'fieldtype' : 'Data',
			'label' : _('Party Name'),
			'width' : 230
		},
		{
			'fieldname' : 'party_contact_no',
			'fieldtype' : 'Phone',
			'label' : _('Party Contact No'),
			'width' : 150
		},
		{
			'fieldname' : 'state',
			'fieldtype' : 'Data',
			'label' : _('State Name'),
			'width' : 120
		},
		{
			'fieldname' : 'destination',
			'fieldtype' : 'Data',
			'label' : _('Destination'),
			'width' : 150
		},
		{
			'fieldname' : 'transporter_name',
			'fieldtype' : 'Data',
			'label' : _('Transporter Name'),
			'width' : 200
		},
		{
			'fieldname' : 'vehicle_no',
			'fieldtype' : 'Data',
			'label' : _('Vehicle No'),
			'width' : 150
		},
		{
			'fieldname' : 'driver_no',
			'fieldtype' : 'Phone',
			'label' : _('Driver No'),
			'width' : 150
		},
		{
			'fieldname' : 'reference',
			'fieldtype' : 'Data',
			'label' : _('Reference'),
			'width' : 150
		},
		{
			'fieldname' : 'tonnage',
			'fieldtype' : 'Float',
			'label' : _('Tonnage'),
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
			'fieldname' : 'invoice_value',
			'fieldtype' : 'Currency',
			'label' : _('Invoice Value'),
			'width' : 150
		},
		{
			'fieldname' : 'invoice_date',
			'fieldtype' : 'Date',
			'label' : _('Invoice Date'),
			'width' : 120
		},
		{
			'fieldname' : 'rate',
			'fieldtype' : 'Currency',
			'label' : _('Rate'),
			'width' : 150
		},
		{
			'fieldname' : 'shipping_address',
			'fieldtype' : 'Small Text',
			'label' : _('Shipping Address'),
			'width' : 150
		},
		{
			'fieldname' : 'transport_req_time',
			'fieldtype' : 'Time',
			'label' : _('Transport REQ Time'),
			'width' : 120
		},
		{
			'fieldname' : 'transport_req_date',
			'fieldtype' : 'Date',
			'label' : _('Transport REQ Date'),
			'width' : 120
		},
		{
			'fieldname' : 'vehicle_request_date',
			'fieldtype' : 'Date',
			'label' : _('Vehicle Request Date'),
			'width' : 120
		},
		{
			'fieldname' : 'vehicle_request_time',
			'fieldtype' : 'Time',
			'label' : _('Vehicle Request Time'),
			'width' : 120
		},
		{
			'fieldname' : 'alloc_time',
			'fieldtype' : 'Time',
			'label' : _('Alloc Time'),
			'width' : 120
		},
		{
			'fieldname' : 'alloc_date',
			'fieldtype' : 'Date',
			'label' : _('Alloc Date'),
			'width' : 120
		},
		{
			'fieldname' : 'dispatch_date',
			'fieldtype' : 'Date',
			'label' : _('Dispatch Date'),
			'width' : 120
		},
		{
			'fieldname' : 'dispatch_time',
			'fieldtype' : 'Time',
			'label' : _('Dispatch Time'),
			'width' : 120
		},
		{
			'fieldname' : 'pod_date',
			'fieldtype' : 'Date',
			'label' : _('POD Date'),
			'width' : 120
		},
		{
			'fieldname' : 'pod_time',
			'fieldtype' : 'Time',
			'label' : _('POD Time'),
			'width' : 120
		},
		{
			'fieldname' : 'pod_status',
			'fieldtype' : 'Data',
			'label' : _('POD Status'),
			'width' : 120
		},
		{
			'fieldname' : 'pod_remarks',
			'fieldtype' : 'Data',
			'label' : _('POD Remarks'),
			'width' : 200
		},
		{
			'fieldname' : 'action_plan',
			'fieldtype' : 'Data',
			'label' : _('Action Plan'),
			'width' : 400
		},
	]

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []
	total_transport_cost = 0
	# Sales Order Data
	dispatch_details = frappe.db.sql(
		f'''
		SELECT 
			so.creation as 'date',
			so.name as 'so_no',
			so.transaction_date as 'transaction_date',
			so.customer  as 'party_name',
			so.contact_person as 'party_contact',
			so.custom_state as 'state',
			so.custom_transport_destination as 'destination',
			so.custom_delivery_time as 'delivery_time',
			so.delivery_date as 'delivery_date',
			so.custom_vehicle_req_datetime as 'vehicle_datetime',
			so.custom_vehicle_type as 'type'
		FROM 
			`tabSales Order` so
		WHERE 
			so.transaction_date  BETWEEN '{conditions.get('from_date')}' AND '{conditions.get('to_date')}'; 
		''',
	as_dict = 1)

	if len(dispatch_details) > 0:
		for detail in dispatch_details:
			# Delivery Note Data
			dn_data = frappe.db.sql(
				f'''
				SELECT 
					dn.name as 'dn_name',
					dn.transporter as 'transporter',
					dn.vehicle_no as 'hired_vehicle',
					dn.custom_hired_vehicle_number as tplNo,
					dn.custom_vehicle_number as 'dedicated_vehicle',
					dn.custom_driver_no as 'driver_no',
					dn.owner as 'reference_name',
					dn.total_net_weight as 'weight',
					dn.shipping_address as 'shipping_address',
					dn.custom_alloc_datetime as 'alloc_dt',
					dn.custom_dispatch_datetime as 'dispatch_dt',
					dn.custom_delivered_datetime as 'pod_datetime',
					dn.custom_pod_status  as 'pod_status',
					dn.custom_pod_remarks as 'pod_remarks',
					dn.custom_action_plan as 'action_plan'
				FROM 
					`tabDelivery Note` dn
				INNER JOIN 
					`tabDelivery Note Item` dni
				WHERE 
					dni.against_sales_order = '{detail.so_no}' AND dn.name  = dni.parent;  
				'''
			, as_dict = 1)
		
			# Sales Invoice Data
			si_data = frappe.db.sql(
				f'''
				SELECT 
					tsi.name ,
					tsi.posting_date,
					tsi.net_total ,
					tsi.custom_transport_cost
				FROM 
					`tabSales Invoice` tsi 
				INNER JOIN 
					`tabSales Invoice Item` tsii
				WHERE 
					tsii.delivery_note = '{dn_data[0].dn_name if dn_data != [] else ''}' 
				AND tsi.name  = tsii.parent 
				AND tsi.is_return != 1
				AND tsi.docstatus = 1; 
				''',
			as_dict = 1)
		
			vehicle = ''
			tonnage = 0
			if dn_data != []:
				# Tonnage Value
				kg = dn_data[0].weight
				tonnage = kg/1000

				# Vehicle Number
				if detail.type == "Dedicated / Company Owned":
					vehicle = dn_data[0].dedicated_vehicle

				elif detail.type  == "Market":
					vehicle = dn_data[0].hired_vehicle
				else:
					vehicle = dn_data[0].hired_vehicle
					
			
			# Main Data Rows
			row = frappe._dict({
				# Sales Order Data
				'so_creation_date' : detail.date,
				'so_number' : detail.so_no,
				'so_transaction_date' : detail.transaction_date,
				'party_name' : detail.party_name,
				'party_contact_no' : frappe.db.get_value('Contact', {'name' : detail.party_contact}, ['mobile_no']) if dn_data != [] else '',
				'state': detail.state,
				'destination' : detail.destination,
				'transport_req_time' : detail.delivery_time,
				'transport_req_date' : detail.delivery_date,
				'vehicle_request_time' : (detail.vehicle_datetime).strftime('%H:%M:%S') if detail.vehicle_datetime != None else '',
				'vehicle_request_date' : detail.vehicle_datetime, 

				# Delivery Note Data
				'transporter_name' : dn_data[0].transporter if dn_data != [] else '',
				'vehicle_no' : vehicle,
				'driver_no' : dn_data[0].driver_no if dn_data != [] else '',
				'reference' : frappe.db.get_value('User', {'name' : dn_data[0].reference_name}, ['full_name']) if dn_data != [] else '',
				'tonnage' : tonnage,
				'shipping_address' : dn_data[0].shipping_address if dn_data != [] else '',
				'alloc_date' : dn_data[0].alloc_dt if dn_data != [] else '',
				'dispatch_date' : dn_data[0].dispatch_dt if dn_data != [] else '',
				'pod_date' : dn_data[0].pod_datetime if dn_data != [] else '',
				'alloc_time' : (dn_data[0].alloc_dt).strftime('%H:%M:%S') if dn_data != [] and dn_data[0].alloc_dt != None else '',
				'dispatch_time' : (dn_data[0].dispatch_dt).strftime('%H:%M:%S') if dn_data != [] and dn_data[0].dispatch_dt != None else '',
				'pod_time' : (dn_data[0].pod_datetime).strftime('%H:%M:%S') if dn_data != [] and dn_data[0].pod_datetime != None else '',
				'pod_status' : dn_data[0].pod_status if dn_data != [] else '',
				'pod_remarks' : dn_data[0].pod_remarks if dn_data != [] else '',
				'action_plan' : dn_data[0].action_plan if dn_data != [] else '',

				# Sales Invoice Data
				'invoice_no' : si_data[0].name if si_data != [] else '',
				'invoice_value' : si_data[0].net_total if si_data != [] else '',
				'invoice_date' : si_data[0].posting_date if si_data != [] else '',
				'rate' : si_data[0].custom_transport_cost if si_data != [] else ''
			})
			total_transport_cost = total_transport_cost + si_data[0].custom_transport_cost if si_data != [] else 0
			data.append(row)

	# Total Row Calcualtion
	row = frappe._dict({
		'party_name' : "TOTAL",
		'rate' : total_transport_cost,
		'tonnage' : None,
		'invoice_value' : None
	})
	data.append(row)
	return data