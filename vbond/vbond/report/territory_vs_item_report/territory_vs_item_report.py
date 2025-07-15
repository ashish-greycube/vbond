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
			"fieldname" : "territory",
			"fieldtype" : "Link",
			"label" : _("Territory"),
			"options" : "Territory",
			"width" : 200
		},
		{
			"fieldname" : "item_group",
			"fieldtype" : "Link",
			"label" : _("Item Group"),
			"options" : "Item Group",
			"width" : 200
		},
		{
			"fieldname" : "item_code",
			"fieldtype" : "Link",
			"label" : _("Item Name"),
			"options" : "Item",
			"width" : 300
		},
		{
			"fieldname" : "qty_sold",
			"fieldtype" : "Float",
			"label" : _("Total Qty Sold"),
			"width" : 200
		},
		{
			"fieldname" : "total_amount",
			"fieldtype" : "Currency",
			"label" : _("Total Sales Amount"),
			"width" : 200
		},
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get('territory'):
		conditions += " AND cust.territory = '{0}'".format(filters.get('territory'))

	if filters.get('item_group'):
		conditions += " AND item.item_group = '{0}'".format(filters.get('item_group'))

	if filters.get('item_name'):
		conditions += " AND sit.item_code = '{0}'".format(filters.get('item_name'))

	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	data = []

	report_data = frappe.db.sql(
		'''
			SELECT cust.territory , item.item_group ,sit.item_code ,sit.item_name, sum(sit.qty) as "qty_sold" ,sum(sit.base_net_amount) as "total_amount"
			FROM `tabSales Invoice` si
			inner join `tabSales Invoice Item` sit
			on si.name=sit.parent 
			inner join `tabCustomer` cust
			on cust.name=si.customer 
			inner join `tabItem` item
			on item.item_code =sit.item_code 
			where si.docstatus=1 AND si.posting_date BETWEEN '{0}' AND '{1}' {2}
			group by  cust.territory , item.item_group ,sit.item_code
		'''.format(filters.get('from_date'), filters.get('to_date'), conditions)
	,as_dict = 1)

	return report_data

