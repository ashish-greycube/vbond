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
		frappe.msgprint("No Data Found")

	return columns, data

def get_columns():
	columns = [
		{
			'fieldname' : 'date',
			'fieldtype' : 'Date',
			'label' : _('Date'),
			'width' : 130
		},
		{
			'fieldname' : 'sales_order_no',
			'fieldtype' : 'Link',
			'label' : _('Sales Order No'),
			'options' : 'Sales Order',
			'width' : 210
		},
		{
			'fieldname' : 'sales_order_date',
			'fieldtype' : 'Date',
			'label' : _('Sales Order Date'),
			'width' : 130
		},
		{
			'fieldname' : 'distributor_name',
			'fieldtype' : 'Data',
			'label' : _('Distributor Name'),
			'width' : 180
		},
		{
			'fieldname' : 'place',
			'fieldtype' : 'Data',
			'label' : _('Place'),
			'width' : 150
		},
		{
			'fieldname' : 'tons',
			'fieldtype' : 'Float',
			'label' : _('Tons'),
			'width' : 130
		},
		{
			'fieldname' : 'vehicle_no',
			'fieldtype' : 'Data',
			'label' : _('Vehicle No'),
			'width' : 150	
		},
		{
			'fieldname' : 'opening_kms',
			'fieldtype' : 'Float',
			'label' : _('Opening KMs'),
			'width' : 130
		},
		{
			'fieldname' : 'closing_kms',
			'fieldtype' : 'Float',
			'label' : _('Closing KMs'),
			'width' : 130
		},
		{
			'fieldname' : 'trip_kms',
			'fieldtype' : 'Float',
			'label' : _('Trip KMs'),
			'width' : 130
		},
		{
			'fieldname' : 'dispatch_date',
			'fieldtype' : 'Date',
			'label' : _('Dispatch Date'),
			'width' : 130
		},
		{
			'fieldname' : 'dispatch_time',
			'fieldtype' : 'Time',
			'label' : _('Dispatch Time'),
			'width' : 130
		},
		{
			'fieldname' : 'arrival_date',
			'fieldtype' : 'Date',
			'label' : _('Arrival Date'),
			'width' : 130
		},
		{
			'fieldname' : 'arrival_time',
			'fieldtype' : 'Time',
			'label' : _('Arrival Time'),
			'width' : 130
		},
		{
			'fieldname' : 'remarks',
			'fieldtype' : 'Float',
			'label' : _('Remarks'),
			'width' : 130
		},
	]
	return columns

def get_conditions(filters):
	condition = ""
	if filters.get('vehicle_number'):
		condition += f"tvl.license_plate = '{filters.get('vehicle_number')}'"

	if filters.get('from_date'):
		condition += f" and tvl.date BETWEEN '{filters.get('from_date')}' AND '{frappe.utils.today()}'"

	if filters.get('from_date') and filters.get('to_date'):
		if filters.get('from_date') > filters.get('to_date'):
			frappe.throw(f"From Date {filters.get('from_date')} Should Be Less Than To Date {filters.get('to_date')}")
		condition += f" and tvl.date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

	return condition

def get_data(filters):
	conditions = get_conditions(filters)
	data = []

	vehicle_entries = frappe.db.sql(
				f'''
					SELECT 
						tvl.date as 'date', 
						tvl.custom_sales_order as 'salesOrder',
						tvl.license_plate as 'vehicleNo',
						tvl.last_odometer as 'openingBalance',
						tvl.odometer as 'closingBalance',
						tvl.custom_arrival_time_date as 'arrivalTimeDate'
					FROM 
						`tabVehicle Log` tvl
					WHERE 
						{conditions}
					ORDER BY
						tvl.date;
				''',
				as_dict = 1, debug = 1)
	
	for entry in vehicle_entries:
		# Converting Weight Into Ton From KG
		weight_in_KG = frappe.db.get_value('Sales Order', {'name' : entry.salesOrder}, fieldname = ['total_net_weight'])
		tons = 0
		if weight_in_KG:
			tons = weight_in_KG / 1000

		dispatch_dt = frappe.db.sql(f'''
			SELECT 
				tdn.posting_date, tdn.posting_time
			FROM 
				`tabDelivery Note Item` tdni
			INNER JOIN
				`tabDelivery Note` tdn 
			WHERE
				tdni.against_sales_order = '{entry.salesOrder}'
			AND 
				tdni.parent = tdn.name;
			''', as_dict = 1)

		row = frappe._dict({
			'date' : entry.date,
			'sales_order_no' : entry.salesOrder,
			'sales_order_date' : frappe.db.get_value('Sales Order', {'name' : entry.salesOrder}, fieldname = ['transaction_date']),
			'distributor_name' : frappe.db.get_value('Sales Order', {'name' : entry.salesOrder}, fieldname = ['customer']),
			'place' : frappe.db.get_value('Sales Order', {'name' : entry.salesOrder}, fieldname = ['custom_transport_destination']),
			'tons': tons,
			'vehicle_no' : entry.vehicleNo,
			'opening_kms' : entry.openingBalance,
			'closing_kms' : entry.closingBalance,
			'trip_kms' : entry.closingBalance - entry.openingBalance,
			'dispatch_date' : dispatch_dt[0].posting_date if dispatch_dt != [] else '',
			'dispatch_time' : dispatch_dt[0].posting_time if dispatch_dt != [] else '',
			'arrival_date' : entry.arrivalTimeDate,
			'arrival_time' : (entry.arrivalTimeDate).strftime("%H:%M:%S") if entry.arrivalTimeDate != None else ''
		})

		data.append(row)

	return data