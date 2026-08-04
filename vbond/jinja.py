import frappe
import erpnext

from frappe.utils import flt, formatdate
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

# from erpnext.accounts.report.general_ledger.general_ledger import execute as gl_execute
# from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute as ar_execute

TOLERANCE = 0.005

def _build_customer_statement(party, party_name, gl_rows, from_date):
    """Pure aggregation: turn one customer's raw GL rows into print-ready statement data."""
    opening_debit = opening_credit = 0.0
    total_row = closing_row = None
    debit_rows, credit_rows = [], []

    voucher_type = ""

    for row in gl_rows:
        # erpnext's get_html() already strips the surrounding quotes from these
        # synthetic rows before handing us `data`, so match on the bare label.
        account = (row.get("account") or "").strip("'")
        if account in ("Opening", "Total", "Closing (Opening + Total)"):
            if account == "Opening":
                opening_debit = flt(row.get("debit"), 2)
                opening_credit = flt(row.get("credit"), 2)
            elif account == "Total":
                total_row = row
            elif account == "Closing (Opening + Total)":
                closing_row = row
            continue

        if row.get("voucher_type") == "Sales Invoice":
            voucher_type = "Sales"
        elif row.get("voucher_type") == "Payment Entry":
            voucher_type = "Bank"
        else :
            voucher_type = row.get("voucher_type")

        entry = {
            "posting_date": formatdate(row.get("posting_date"), "d-MMM-yy"),
            # "particulars": "PARTICULARS",
            "particulars": f"{voucher_type} {row.get('against_voucher') or ""}",
            "voucher_type": row.get("voucher_type"),
            "voucher_no": row.get("voucher_no"),
        }
        debit, credit = flt(row.get("debit"), 2), flt(row.get("credit"), 2)
        if debit > TOLERANCE:
            debit_rows.append({**entry, "amount": debit})
        if credit > TOLERANCE:
            credit_rows.append({**entry, "amount": credit})

    opening_diff = flt(opening_debit - opening_credit, 2)
    if opening_diff > TOLERANCE:
        debit_rows.insert(0, {"posting_date": formatdate(from_date, "d-MMM-yy"), "particulars": "Opening Balance",
                               "voucher_type": "", "voucher_no": "", "amount": opening_diff})
    elif opening_diff < -TOLERANCE:
        credit_rows.insert(0, {"posting_date": "", "particulars": "Opening Balance",
                                "voucher_type": "", "voucher_no": "", "amount": abs(opening_diff)})

    total_debit = flt(total_row.get("debit"), 2) if total_row else 0.0
    total_credit = flt(total_row.get("credit"), 2) if total_row else 0.0
    balance = flt(total_row.get("balance"), 2) if total_row else 0.0
    if balance < -TOLERANCE:
        closing_side, closing_balance = "Debit", abs(balance)
    elif balance > TOLERANCE:
        closing_side, closing_balance = "Credit", balance
    else:
        closing_side, closing_balance = None, 0.0

    grand_total_debit = flt(closing_row.get("debit"), 2) if closing_row else 0.0
    grand_total_credit = flt(closing_row.get("credit"), 2) if closing_row else 0.0
    grand_total_balance = flt(closing_row.get("balance"), 2) if closing_row else 0.0

    return {
        "party": party,
        "party_name": party_name,
        "debit_rows": debit_rows,
        "credit_rows": credit_rows,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "closing_balance": closing_balance,
        "closing_side": closing_side,
        "grand_total_debit": grand_total_debit,
        "grand_total_credit": grand_total_credit,
        "grand_total_balance": grand_total_balance,
    }

def _build_customer_accounts_receivable(party, party_name, ar_rows):
    """Pure aggregation: turn one customer's raw AR rows into print-ready statement data.

    Unlike the GL report, AR rows are a flat snapshot as of report_date - there's no
    synthetic Opening/Total/Closing row and no opening balance to carry forward.
    """
    debit_rows, credit_rows = [], []

    for row in ar_rows:
        voucher_type = "Sales" if row.get("voucher_type") == "Sales Invoice" else (row.get("voucher_type") or "")

        entry = {
            "posting_date": formatdate(row.get("posting_date"), "d-MMM-yy"),
            "particulars": f"{voucher_type} {row.get('voucher_no')}",
            "voucher_type": row.get("voucher_type"),
            "voucher_no": row.get("voucher_no"),
        }
        debit, credit = flt(row.get("invoiced"), 2), flt(row.get("paid"), 2)
        if debit > TOLERANCE:
            debit_rows.append({**entry, "amount": debit})
        if credit > TOLERANCE:
            credit_rows.append({**entry, "amount": credit})

    total_debit = flt(sum(r["amount"] for r in debit_rows), 2)    # Count total debit by sum
    total_credit = flt(sum(r["amount"] for r in credit_rows), 2)  # Count total credit by sum
    balance = flt(total_debit - total_credit, 2)                  # Count total balance by sum
    if balance < -TOLERANCE:
        closing_side, closing_balance = "Debit", abs(balance)
    elif balance > TOLERANCE:
        closing_side, closing_balance = "Credit", balance
    else:
        closing_side, closing_balance = None, 0.0

    return {
        "party": party,
        "party_name": party_name,
        "debit_rows": debit_rows,
        "credit_rows": credit_rows,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "closing_balance": closing_balance,
        "closing_side": closing_side,
        "grand_total_debit": total_debit,
        "grand_total_credit": total_credit,
        "grand_total_balance": balance,
    }


def get_report_data_for_print(report_name, filters, data):
    """Jinja method for the "Process Statement of Accounts" print format.

    erpnext.accounts.doctype.process_statement_of_accounts.get_html() calls this
    once per customer, passing the filters/rows it already built for that
    customer's GL/AR report - no doc, no re-running the report.
    """
    party = (filters.get("party") or [None])[0]
    party_name = (
        filters.get("customer_name")
        or (filters.get("party_name") or [None])[0]
        or frappe.get_cached_value("Customer", party, "customer_name")
        or party
    )

    if report_name == "General Ledger":
        return _build_customer_statement(party, party_name, data or [], filters.get("from_date"))
    return _build_customer_accounts_receivable(party, party_name, data or [])
