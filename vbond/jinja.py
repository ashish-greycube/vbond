import frappe 
import erpnext

from hrms.hr.report.leave_ledger.leave_ledger import execute as execute_

def get_leaves_from_leave_ledger_in_salary_slip(doc):
    leave_data = {}
    
    filters = {
        "from_date": doc.start_date,
        "to_date" : doc.end_date,
        "employee" : doc.employee,
        "company" : doc.company,
        "transaction_type" : "Leave Application"
    }
    response = execute_(filters)
    if response != None or response != []:
        data = response[1]
        if data != []:
            leave_data = data[-1]
    return leave_data