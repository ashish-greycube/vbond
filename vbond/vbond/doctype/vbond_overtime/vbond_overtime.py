# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document

class VbondOvertime(Document):
	def on_submit(self):
		self.create_additional_salary_for_overtime()

	def create_additional_salary_for_overtime(self):
		company = erpnext.get_default_company()
		overtime_salary_component = frappe.db.get_single_value("Vbond Settings", "default_overtime_salary_component")
		if overtime_salary_component == None:
			frappe.throw("Please Assign Default Overtime Salary Component In Vbond Settings.")
		salary_assignment = frappe.db.get_all(
			doctype = "Salary Structure Assignment",
			filters = {
				"employee" : self.employee,
				"company" : company,
				"docstatus": 1,
			},
			fields = ["name"],
			order_by = "from_date"
		)
		print(salary_assignment)
		if salary_assignment != []:
			overtime_amount = 0
			base = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "base")
			print(base)
			if base != None:
				overtime_amount = (base / 30) * self.overtime_days 
			else:
				overtime_amount = 0

			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = self.employee
			additional_salary.company = company
			additional_salary.payroll_date = self.payroll_date
			additional_salary.salary_component = overtime_salary_component
			additional_salary.currency = frappe.db.get_value("Company", company, "default_currency")
			additional_salary.overwrite_salary_structure_amount = 1
			additional_salary.amount = overtime_amount

			additional_salary.save(ignore_permissions=True)
			frappe.msgprint("Additional Salary {0} Created For Employee {1}".format(frappe.utils.get_link_to_form("Additional Salary", additional_salary.name), self.employee), alert=True)
		elif salary_assignment == []: 
			frappe.throw("Salary Assignment Not Found For Employee")