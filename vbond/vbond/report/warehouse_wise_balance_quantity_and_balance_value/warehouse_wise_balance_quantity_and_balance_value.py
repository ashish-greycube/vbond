# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from erpnext.stock.report.stock_balance.stock_balance import execute as sb_execute


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	filters["item_code"] = [filters.get("item_code")] if filters.get("item_code") else []

	columns = get_columns()
	data = get_data(filters)

	return columns, data

def execute_snapshot_report(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for snapshot report. When 'Synced
	Report' is enabled in report, framework will call this method
	every time the report is refreshed or a filter is updated. It
	accepts the same filters as normal execute. But a utility method -
	get_latest_sync, is also imported.

	"""
	from frappe.database.duckdb.database import get_latest_sync

	columns = get_columns()
	data = get_data()

	return columns, data

def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"label": _("Sum of Balance Qty"),
			"fieldname": "balance_qty",
			"fieldtype": "Float",
		},
		{
			"label": _("Sum of Balance Value"),
			"fieldname": "balance_value",
			"fieldtype": "Currency",
		},
	]


def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""

	stock_balance_report = sb_execute(filters)
	stock_balance_data = stock_balance_report[1] if len(stock_balance_report) > 1 else []

	data = []
	warehouse_list = frappe.db.sql("SELECT name FROM `tabWarehouse`", as_dict=True, pluck="name")
	
	for wh in warehouse_list:
		wh_balance_qty = 0
		wh_balance_value = 0
		for row in stock_balance_data:
			if row.get("warehouse") == wh:
				wh_balance_qty += row.get("bal_qty")
				wh_balance_value += row.get("bal_val")
				
		if wh_balance_qty or wh_balance_value:
			data.append({
					"warehouse": wh,
					"balance_qty": wh_balance_qty,
					"balance_value": wh_balance_value,
				})				

	return data
