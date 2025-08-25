# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from itertools import groupby
from calendar import monthrange
from frappe.utils import cint, cstr, getdate
from frappe.utils.nestedset import get_descendants_of
from frappe.query_builder.functions import Count, Extract, Sum

def execute(filters=None):
	if not filters: 
		filters = {}
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			'fieldname' : 'employee',
			'fieldtype' : 'Link',
			'label' : _('Employee'),
			'options' : 'Employee',
			'width' : 250,
		},
		{
			'fieldname' : 'detail',
			'fieldtype' : 'Data',
			'label' : _('Detail Type'),
			'width' : 130,
		},
	]

	total_days = frappe.utils.date_diff(frappe.utils.getdate(filters.get('to_date')), frappe.utils.getdate(filters.get('from_date')))

	i = 1
	for day in range(0, total_days+1):
		dayname = frappe.utils.getdate(frappe.utils.add_to_date(filters.get('from_date'), days=day)).strftime("%a")
		day = cint(frappe.utils.getdate(frappe.utils.add_to_date(filters.get('from_date'), days=day)).strftime("%d"))
		
		col = {
			'fieldname' : i,
			'fieldtype' : 'Data',
			'label' : "{0} {1}".format(day, dayname),
			'width' : 100,
		}
		columns.append(col)
		i = i + 1
	
	columns.append({
		'fieldname' : 'total',
		'fieldtype' : 'Data',
		'label' : _('Total'),
		'width' : 130,
	})
	return columns

def get_conditions(filters):
	condition = ""
	return condition

def get_data(filters):
	# Reference Report Data
	data = get_monthly_attendance_sheet_report_data(filters)
	data = data[1]
	# print(data)
	# Creating Employee Attendance Map For Optimazation
	employee_times_map = {} 
	end_date = filters.get('to_date') ,
	start_date =  filters.get('from_date')

	employee_times = frappe.db.sql("""
		select employee , in_time , out_time , late_entry , early_exit , working_hours , attendance_date, shift, department, employee_name
		from tabAttendance ta 
		where attendance_date between %s and %s
		order by employee
	""",(start_date , end_date), as_dict = True)

	for d in employee_times:
		employee_times_map[d['employee']+ "-" +str(int(getdate(d['attendance_date']).strftime('%d')))] = d
	

	# For Each Employee Finding Daywise Map + Assigning Status 
	for d in data:
		for col in d:
			if col in ['shift', 'employee', 'employee_name']:
				continue

			if not 'employee' in d:
				continue

			status = d[col]
			no_attendance_dict = {
				"employee": d['employee'],
				"in_time":None,
				"out_time":None,
				"late_entry":0,
				"early_exit":0,
				"working_hours":0.0,
				"shift" : None,
				"department" : None
			}
			d[col] = employee_times_map[d['employee']+ "-" +col] if d['employee']+ "-" +col in employee_times_map else no_attendance_dict
			d[col]['status'] = status

	# Converting Data Into Employee Wise Dict
	report_output = {}
	for d in data:
		if not 'employee' in d:
			continue
		report_output[d['employee']] = []
		for col in d:
			if col in ['shift', 'employee', 'employee_name']:
				continue
			d[col].update({
				"employee_name" : d['employee_name']
			})
			report_output[d['employee']].append(d[col])
			
	# Converting Report Data Into Rows By Detail Type
	report_rows = []
	for out in report_output:
		in_row = {'employee':out, 'employee_name':report_output[out][0]['employee_name'],  'detail': 'In Time', 'shift' :report_output[out][0]['shift'], 'department' :report_output[out][0]['department'] }
		out_row = {'hidden_employee':out, 'detail': 'Out Time', 'shift' : report_output[out][0]['shift'], 'department' :report_output[out][0]['department']}
		hrs_row = {'hidden_employee':out, 'detail': 'Total Hrs', 'shift' : report_output[out][0]['shift'], 'department' :report_output[out][0]['department'], 'total' : 0}
		sts_row = {'hidden_employee':out, 'detail': 'Status', 'shift' : report_output[out][0]['shift'], 'department' :report_output[out][0]['department'], 'total' : 0}
		day = 1
		for d in report_output[out]:
			in_row[day] = frappe.format(d['in_time'], "Time")
			out_row[day] = frappe.format(d['out_time'], "Time")
			hrs_row[day] = d['working_hours']
			hrs_row['total'] = round(hrs_row['total'] + d['working_hours'], 2)
			sts_row[day] = d['status']
			sts_row['total'] = round((sts_row['total'] + 1), 2) if d['status'] == "P" else round(sts_row['total'], 2)
			day = day + 1
		report_rows.append(in_row)
		report_rows.append(out_row)
		report_rows.append(hrs_row)
		report_rows.append(sts_row)
	
	if filters:
		keys = list(filters.keys())
		if keys == ['from_date', 'to_date']:
			return report_rows
		report_rows = get_filtered_data(filters, report_rows)

	return report_rows


def get_filtered_data(filters, report_rows):
	filtered_data = []
	print(report_rows)
	if filters.get("shift") and filters.get('employee') and  filters.get("department"):
		for rr in report_rows:
			if (rr['shift'] == filters.get("shift")) and ('employee' in rr and rr['employee'] == filters.get("employee")) or ('hidden_employee' in rr and rr['hidden_employee'] == filters.get("employee")) and (rr['department'] == filters.get("department")):
				filtered_data.append(rr)
		return filtered_data

	if filters.get("shift") and filters.get('employee'):
		for rr in report_rows:
			if (rr['shift'] == filters.get("shift")) and ('employee' in rr and rr['employee'] == filters.get("employee")) or ('hidden_employee' in rr and rr['hidden_employee'] == filters.get("employee")):
				filtered_data.append(rr)
		return filtered_data
	
	if filters.get("shift") and filters.get('department'):
		for rr in report_rows:
			if (rr['shift'] == filters.get("shift")) and (rr['department'] == filters.get("department")):
				filtered_data.append(rr)
		return filtered_data

	if filters.get("shift"):
		for rr in report_rows:
			if rr['shift'] == filters.get("shift"):
				filtered_data.append(rr)
		return filtered_data

	if filters.get('employee'):
		for rr in report_rows:
			if ('employee' in rr and rr['employee'] == filters.get("employee")) or ('hidden_employee' in rr and rr['hidden_employee'] == filters.get("employee")):
				filtered_data.append(rr)
		return filtered_data
	
	if filters.get("department"):
		for rr in report_rows:
			if rr['department'] == filters.get("department"):
				filtered_data.append(rr)
		return filtered_data




def get_monthly_attendance_sheet_report_data(filters):
	ref_filters = frappe._dict({
		'from_date' : filters.get('from_date'),
		'to_date' : filters.get('to_date'),
		'month' : frappe.utils.getdate(filters.get('from_date')).strftime("%b"),
		'year' : frappe.utils.getdate(filters.get('from_date')).strftime("%Y"),
		'company' : erpnext.get_default_company(),
		'include_company_descendants' : 1,
	})

	Filters = ref_filters

	status_map = {
		"Present": "P",
		"Absent": "A",
		"Half Day": "HD",
		"Work From Home": "WFH",
		"On Leave": "L",
		"Holiday": "H",
		"Weekly Off": "WO",
	}

	day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


	def _execute(filters: Filters) -> tuple:
		filters = frappe._dict(filters or {})
	
		if not (filters.month and filters.year):
			frappe.throw(_("Please select month and year."))

		if not filters.company:
			frappe.throw(_("Please select company."))

		if filters.company:
			filters.companies = [filters.company]
			if filters.include_company_descendants:
				filters.companies.extend(get_descendants_of("Company", filters.company))

		attendance_map = get_attendance_map(filters)
		if not attendance_map:
			frappe.msgprint(_("No attendance records found."), alert=True, indicator="orange")
			return [], [], None, None

		columns = get_columns(filters)
		data = get_data(filters, attendance_map)

		if not data:
			frappe.msgprint(_("No attendance records found for this criteria."), alert=True, indicator="orange")
			return columns, [], None, None
		# print("============================================================================")
		# print(data)
		return columns, data


	def get_columns(filters: Filters) -> list[dict]:
		columns = []
		columns.extend(
			[
				{
					"label": _("Employee"),
					"fieldname": "employee",
					"fieldtype": "Link",
					"options": "Employee",
					"width": 135,
				},
				{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 120},
			]
		)
		columns.append({"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 120})
		# columns.extend(get_columns_for_days(filters))

		return columns


	def get_columns_for_leave_types() -> list[dict]:
		leave_types = frappe.db.get_all("Leave Type", pluck="name")
		types = []
		for entry in leave_types:
			types.append({"label": entry, "fieldname": frappe.scrub(entry), "fieldtype": "Float", "width": 120})

		return types


	def get_columns_for_days(filters: Filters) -> list[dict]:
		total_days = get_total_days_in_month(filters)
		days = []

		for day in range(1, total_days + 1):
			day = cstr(day)
			# forms the dates from selected year and month from filters
			date = f"{cstr(filters.year)}-{cstr(filters.month)}-{day}"
			# gets abbr from weekday number
			weekday = day_abbr[getdate(date).weekday()]
			# sets days as 1 Mon, 2 Tue, 3 Wed
			label = f"{day} {weekday}"
			days.append({"label": label, "fieldtype": "Data", "fieldname": day, "width": 65})

		return days


	def get_total_days_in_month(filters: Filters) -> int:
		# return monthrange(cint(filters.year), cint(frappe.utils.getdate(filters.get('from_date')).strftime("%m")))[1]
		return frappe.utils.date_diff(frappe.utils.getdate(filters.get('to_date')), frappe.utils.getdate(filters.get('from_date')))

	def get_data(filters: Filters, attendance_map: dict) -> list[dict]:
		employee_details, group_by_param_values = get_employee_related_details(filters)
		holiday_map = get_holiday_map(filters)
		data = []

		data = get_rows(employee_details, filters, holiday_map, attendance_map)

		return data


	def get_attendance_map(filters: Filters) -> dict:
		"""Returns a dictionary of employee wise attendance map as per shifts for all the days of the month like
		{
			'employee1': {
					'Morning Shift': {1: 'Present', 2: 'Absent', ...}
					'Evening Shift': {1: 'Absent', 2: 'Present', ...}
			},
			'employee2': {
					'Afternoon Shift': {1: 'Present', 2: 'Absent', ...}
					'Night Shift': {1: 'Absent', 2: 'Absent', ...}
			},
			'employee3': {
					None: {1: 'On Leave'}
			}
		}
		"""
		
		attendance_list = get_attendance_records(filters)
		
		attendance_map = {}
		leave_map = {}

		for d in attendance_list:
			if d.status == "On Leave":
				leave_map.setdefault(d.employee, {}).setdefault(d.shift, []).append(d.day_of_month)
				continue

			if d.shift is None:
				d.shift = ""

			attendance_map.setdefault(d.employee, {}).setdefault(d.shift, {})
			attendance_map[d.employee][d.shift][d.day_of_month] = d.status

		# leave is applicable for the entire day so all shifts should show the leave entry
		for employee, leave_days in leave_map.items():
			for assigned_shift, days in leave_days.items():
				# no attendance records exist except leaves
				if employee not in attendance_map:
					attendance_map.setdefault(employee, {}).setdefault(assigned_shift, {})

				for day in days:
					for shift in attendance_map[employee].keys():
						attendance_map[employee][shift][day] = "On Leave"
	
		return attendance_map


	def get_attendance_records(filters: Filters) -> list[dict]:
		Attendance = frappe.qb.DocType("Attendance")
		query = (
			frappe.qb.from_(Attendance)
			.select(
				Attendance.employee,
				Extract("day", Attendance.attendance_date).as_("day_of_month"),
				Attendance.status,
				Attendance.shift,
				Attendance.in_time,
				Attendance.out_time,
				Attendance.late_entry,
				Attendance.early_exit,
				Attendance.working_hours,
			)
			.where(
				(Attendance.docstatus == 1)
				& (Attendance.company.isin(filters.companies))
				& (Attendance.attendance_date >= frappe.utils.getdate(filters.get('from_date')))
				& (Attendance.attendance_date <= frappe.utils.getdate(filters.get('to_date')))
			)
		)

		if filters.employee:
			query = query.where(Attendance.employee == filters.employee)
		query = query.orderby(Attendance.employee, Attendance.attendance_date)

		return query.run(as_dict=1)


	def get_employee_related_details(filters: Filters) -> tuple[dict, list]:
		"""Returns
		1. nested dict for employee details
		2. list of values for the group by filter
		"""
		Employee = frappe.qb.DocType("Employee")
		query = (
			frappe.qb.from_(Employee)
			.select(
				Employee.name,
				Employee.employee_name,
				Employee.designation,
				Employee.grade,
				Employee.department,
				Employee.branch,
				Employee.company,
				Employee.holiday_list,
			)
			.where(Employee.company.isin(filters.companies))
		)

		if filters.employee:
			query = query.where(Employee.name == filters.employee)

		employee_details = query.run(as_dict=True)

		group_by_param_values = []
		emp_map = {}

		for emp in employee_details:
			emp_map[emp.name] = emp

		return emp_map, group_by_param_values


	def get_holiday_map(filters: Filters) -> dict[str, list[dict]]:
		"""
		Returns a dict of holidays falling in the filter month and year
		with list name as key and list of holidays as values like
		{
				'Holiday List 1': [
						{'day_of_month': '0' , 'weekly_off': 1},
						{'day_of_month': '1', 'weekly_off': 0}
				],
				'Holiday List 2': [
						{'day_of_month': '0' , 'weekly_off': 1},
						{'day_of_month': '1', 'weekly_off': 0}
				]
		}
		"""
		# add default holiday list too
		holiday_lists = frappe.db.get_all("Holiday List", pluck="name")
		default_holiday_list = frappe.get_cached_value("Company", filters.company, "default_holiday_list")
		holiday_lists.append(default_holiday_list)

		holiday_map = frappe._dict()
		Holiday = frappe.qb.DocType("Holiday")

		for d in holiday_lists:
			if not d:
				continue

			holidays = (
				frappe.qb.from_(Holiday)
				.select(Extract("day", Holiday.holiday_date).as_("day_of_month"), Holiday.weekly_off)
				.where(
					(Holiday.parent == d)
					& (Holiday.holiday_date >= frappe.utils.getdate(filters.get("from_date")))
					& (Holiday.holiday_date <= frappe.utils.getdate(filters.get("to_date")))
				)
			).run(as_dict=True)

			holiday_map.setdefault(d, holidays)

		return holiday_map


	def get_rows(employee_details: dict, filters: Filters, holiday_map: dict, attendance_map: dict) -> list[dict]:
		records = []
		default_holiday_list = frappe.get_cached_value("Company", filters.company, "default_holiday_list")

		for employee, details in employee_details.items():
			emp_holiday_list = details.holiday_list or default_holiday_list
			holidays = holiday_map.get(emp_holiday_list)

			employee_attendance = attendance_map.get(employee)
			if not employee_attendance:
				continue
			# print(employee_attendance)
			attendance_for_employee = get_attendance_status_for_detailed_view(
				employee, filters, employee_attendance, holidays
			)
			# set employee details in the first row
			attendance_for_employee[0].update({"employee": employee, "employee_name": details.employee_name})

			records.extend(attendance_for_employee)
		return records


	def set_defaults_for_summarized_view(filters, row):
		for entry in get_columns(filters):
			if entry.get("fieldtype") == "Float":
				row[entry.get("fieldname")] = 0.0


	def get_attendance_status_for_summarized_view(employee: str, filters: Filters, holidays: list) -> dict:
		"""Returns dict of attendance status for employee like
		{'total_present': 1.5, 'total_leaves': 0.5, 'total_absent': 13.5, 'total_holidays': 8, 'unmarked_days': 5}
		"""
		summary, attendance_days = get_attendance_summary_and_days(employee, filters)
		if not any(summary.values()):
			return {}

		total_days = get_total_days_in_month(filters)
		total_holidays = total_unmarked_days = 0

		for day in range(1, total_days + 1):
			if day in attendance_days:
				continue

			status = get_holiday_status(day, holidays)
			if status in ["Weekly Off", "Holiday"]:
				total_holidays += 1
			elif not status:
				total_unmarked_days += 1

		return {
			"total_present": summary.total_present + summary.total_half_days,
			"total_leaves": summary.total_leaves + summary.total_half_days,
			"total_absent": summary.total_absent,
			"total_holidays": total_holidays,
			"unmarked_days": total_unmarked_days,
		}


	def get_attendance_summary_and_days(employee: str, filters: Filters) -> tuple[dict, list]:
		Attendance = frappe.qb.DocType("Attendance")

		present_case = (
			frappe.qb.terms.Case()
			.when(((Attendance.status == "Present") | (Attendance.status == "Work From Home")), 1)
			.else_(0)
		)
		sum_present = Sum(present_case).as_("total_present")

		absent_case = frappe.qb.terms.Case().when(Attendance.status == "Absent", 1).else_(0)
		sum_absent = Sum(absent_case).as_("total_absent")

		leave_case = frappe.qb.terms.Case().when(Attendance.status == "On Leave", 1).else_(0)
		sum_leave = Sum(leave_case).as_("total_leaves")

		half_day_case = frappe.qb.terms.Case().when(Attendance.status == "Half Day", 0.5).else_(0)
		sum_half_day = Sum(half_day_case).as_("total_half_days")

		summary = (
			frappe.qb.from_(Attendance)
			.select(
				sum_present,
				sum_absent,
				sum_leave,
				sum_half_day,
			)
			.where(
				(Attendance.docstatus == 1)
				& (Attendance.employee == employee)
				& (Attendance.company.isin(filters.companies))
				& (Extract("month", Attendance.attendance_date) == filters.month)
				& (Extract("year", Attendance.attendance_date) == filters.year)
			)
		).run(as_dict=True)

		days = (
			frappe.qb.from_(Attendance)
			.select(Extract("day", Attendance.attendance_date).as_("day_of_month"))
			.distinct()
			.where(
				(Attendance.docstatus == 1)
				& (Attendance.employee == employee)
				& (Attendance.company.isin(filters.companies))
				& (Extract("month", Attendance.attendance_date) == filters.month)
				& (Extract("year", Attendance.attendance_date) == filters.year)
			)
		).run(pluck=True)

		return summary[0], days


	def get_attendance_status_for_detailed_view(
		employee: str, filters: Filters, employee_attendance: dict, holidays: list
	) -> list[dict]:
		"""Returns list of shift-wise attendance status for employee
		[
				{'shift': 'Morning Shift', 1: 'A', 2: 'P', 3: 'A'....},
				{'shift': 'Evening Shift', 1: 'P', 2: 'A', 3: 'P'....}
		]
		"""
		total_days = get_total_days_in_month(filters)
		attendance_values = []
		
		for shift, status_dict in employee_attendance.items():
			row = {"shift": shift}
			
			for day in range(0, total_days+1):
				day = cint(frappe.utils.getdate(frappe.utils.add_to_date(filters.get('from_date'), days=day)).strftime("%d"))
				# print(day)
				status = status_dict.get(day)
				if status is None and holidays:
					status = get_holiday_status(day, holidays)

				abbr = status_map.get(status, "")
				row[cstr(day)] = abbr

			attendance_values.append(row)

		return attendance_values


	def get_holiday_status(day: int, holidays: list) -> str:
		status = None
		if holidays:
			for holiday in holidays:
				if day == holiday.get("day_of_month"):
					if holiday.get("weekly_off"):
						status = "Weekly Off"
					else:
						status = "Holiday"
					break
		return status


	def get_leave_summary(employee: str, filters: Filters) -> dict[str, float]:
		"""Returns a dict of leave type and corresponding leaves taken by employee like:
		{'leave_without_pay': 1.0, 'sick_leave': 2.0}
		"""
		Attendance = frappe.qb.DocType("Attendance")
		day_case = frappe.qb.terms.Case().when(Attendance.status == "Half Day", 0.5).else_(1)
		sum_leave_days = Sum(day_case).as_("leave_days")

		leave_details = (
			frappe.qb.from_(Attendance)
			.select(Attendance.leave_type, sum_leave_days)
			.where(
				(Attendance.employee == employee)
				& (Attendance.docstatus == 1)
				& (Attendance.company.isin(filters.companies))
				& ((Attendance.leave_type.isnotnull()) | (Attendance.leave_type != ""))
				& (Extract("month", Attendance.attendance_date) == filters.month)
				& (Extract("year", Attendance.attendance_date) == filters.year)
			)
			.groupby(Attendance.leave_type)
		).run(as_dict=True)

		leaves = {}
		for d in leave_details:
			leave_type = frappe.scrub(d.leave_type)
			leaves[leave_type] = d.leave_days

		return leaves


	def get_entry_exits_summary(employee: str, filters: Filters) -> dict[str, float]:
		"""Returns total late entries and total early exits for employee like:
		{'total_late_entries': 5, 'total_early_exits': 2}
		"""
		Attendance = frappe.qb.DocType("Attendance")

		late_entry_case = frappe.qb.terms.Case().when(Attendance.late_entry == "1", "1")
		count_late_entries = Count(late_entry_case).as_("total_late_entries")

		early_exit_case = frappe.qb.terms.Case().when(Attendance.early_exit == "1", "1")
		count_early_exits = Count(early_exit_case).as_("total_early_exits")

		entry_exits = (
			frappe.qb.from_(Attendance)
			.select(count_late_entries, count_early_exits)
			.where(
				(Attendance.docstatus == 1)
				& (Attendance.employee == employee)
				& (Attendance.company.isin(filters.companies))
				& (Extract("month", Attendance.attendance_date) == filters.month)
				& (Extract("year", Attendance.attendance_date) == filters.year)
			)
		).run(as_dict=True)

		return entry_exits[0]


	@frappe.whitelist()
	def get_attendance_years() -> str:
		"""Returns all the years for which attendance records exist"""
		Attendance = frappe.qb.DocType("Attendance")
		year_list = (
			frappe.qb.from_(Attendance).select(Extract("year", Attendance.attendance_date).as_("year")).distinct()
		).run(as_dict=True)

		if year_list:
			year_list.sort(key=lambda d: d.year, reverse=True)
		else:
			year_list = [frappe._dict({"year": getdate().year})]

		return "\n".join(cstr(entry.year) for entry in year_list)
	
	result = _execute(Filters)

	return result
