import frappe
from frappe import _
import erpnext
import json
from frappe.utils import flt, get_link_to_form
from erpnext.buying.report.item_wise_purchase_history.item_wise_purchase_history import execute 

# Function For Filtering Destination Based On State
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def filter_destination(doctype, txt, searchfield, start, page_len, filters):
    if filters: 
        state = filters.get('state')
    destinations = frappe.get_all("Vbond Final Rate Card", {'state' : state, "name": ("like", "%%%s%%" % txt),}, 'destination',  order_by = 'destination', as_list = 1)
    return destinations

# Function For Calculating Range Of MT Weight in SO, SI and DN
def get_mt_weight_range(weight, state):
    mt_weight = ""
    if state in ['Andhra Pradesh', 'Tamilnadu', 'Karnataka'] and weight > 0.0 and weight <= 8.0:
        mt_weight = "6_8_mt"
    
    elif state in ['Tamilnadu', 'Karnataka'] and weight > 12.0 and weight <= 16.0:
        mt_weight = "12_16_mt"

    elif weight > 0 and weight <= 6.0:
        mt_weight = "0_6_mt"

    elif weight > 6.0 and  weight <= 8.0:
        mt_weight = "6_8_mt"

    elif weight > 8.0 and weight <= 10.0:
        mt_weight = "8_10_mt"

    elif weight > 10.0 and weight <= 12.0:
        mt_weight = "10_12_mt"

    elif weight > 12.0 and weight <= 15.0:
        mt_weight = "12_15_mt"

    elif weight > 15.0 and weight <= 18.0:
        mt_weight = "15_18_mt"

    elif weight > 18.0 and weight <= 20.0:
        mt_weight = "18_20_mt"

    elif weight > 20.0 and weight <= 25.0:
        mt_weight = "20_25_mt"

    elif weight > 25.0 and weight <= 30.0:
        mt_weight = "25_30_mt"

    elif weight > 30.0 and state != "HYD":
        mt_weight = "25_30_mt"

    elif weight > 30.0 and weight <= 35.0:
        mt_weight = "30_35_mt"

    elif weight > 35.0 and weight <= 40.0:
        mt_weight = "35_40_mt"
    
    elif weight > 40.0 and state == "HYD":
        mt_weight = "35_40_mt"

    return mt_weight

# Function For Calculation Transport Data In SO
def calculate_transport_data(self, method):
    vehicle_no = self.custom_vehicle_number
    vehicle_type = self.custom_vehicle_type

    # Total Tonnage Value For SO, SI & DN
    if len(self.items) > 0:
        kg_weight = self.total_net_weight
        if kg_weight > 0:
            tonnage_weight = kg_weight / 1000
            self.custom_total_tonnage = tonnage_weight

    if vehicle_type == "Dedicated / Company Owned":
        if vehicle_no != None:
            rate_per_km = frappe.db.get_value(
                doctype = "Vehicle",
                filters = {'name' : vehicle_no},
                fieldname = ['custom_rate_per_km']
            )

            self.custom_transport_rate_per_km = rate_per_km

        transport_distance = self.custom_destination_distance
        transport_rate = self.custom_transport_rate_per_km

        if transport_distance and transport_rate > 0:
            transport_cost = (transport_distance * transport_rate)
            self.custom_transport_cost = transport_cost

    elif vehicle_type == "Market":
        state = self.custom_state
        destination = self.custom_transport_destination
        kg_weight = self.total_net_weight

        if kg_weight == 0:
            self.custom_transport_cost = 0
            frappe.msgprint("Total Transport Cost is 0 as Total Net Weight is 0 KG", alert=True, indicator="blue")
            return
        
        elif kg_weight > 0:
            metric_weight = (kg_weight / 1000)
            mt_weight_range = get_mt_weight_range(metric_weight, state)
            
            if state and destination != None:
                transport_cost = frappe.db.get_value(
                    doctype = "Vbond Final Rate Card",
                    filters = {
                        'destination' : destination,
                        'state' : state
                    },
                    fieldname = [mt_weight_range]
                )

                distance = frappe.db.get_value(
                    doctype = "Vbond Final Rate Card",
                    filters = {
                        'destination' : destination,
                        'state' : state
                    },
                    fieldname = ['kms']
                )
            
                self.custom_destination_distance = distance
                self.custom_transport_cost = transport_cost

    # Moving Vehicle Number From Details To Transfer Section
    if vehicle_type == "Dedicated / Company Owned":
            if self.doctype == "Sales Order":
                vehicle_num = self.custom_vehicle_number
                self.vehicle_no = vehicle_num

            elif self.doctype == "Delivery Note" or self.doctype == "Sales Invoice":
                if self.vehicle_no == None:
                    vehicle_num = self.custom_vehicle_number
                    self.vehicle_no = vehicle_num

    elif vehicle_type == "Market" or vehicle_type == "TPL(Third Party Logistics)":
            if self.doctype == "Sales Order":
                    vehicle_num = self.custom_hired_vehicle_number
                    self.vehicle_no = vehicle_num

            elif self.doctype == "Delivery Note" or self.doctype == "Sales Invoice":
                if self.vehicle_no == None:
                    vehicle_num = self.custom_hired_vehicle_number
                    self.vehicle_no = vehicle_num
                    self.custom_hired_vehicle_number = None

# Calculation of Basic Amount
def calculate_basic_amount(self, method):
    basic_amount = 0
    if len(self.items) > 0:
        for item in self.items:
            incoming_rate = item.incoming_rate
            qty = item.qty

            basic_item_amount = incoming_rate * qty
            basic_amount += basic_item_amount
        self.custom_basic_amount = basic_amount


# Calculation Of Trip Km In Vehicle Log
def calculate_trip_km(self, method):
    current_odometer = self.odometer
    last_odometer = self.last_odometer

    if current_odometer > last_odometer:
        current_trip_km = current_odometer - last_odometer
        self.custom_trip_km = current_trip_km

# Creation Of Serial Batch No Feature
def generate_and_set_batch_no(self, method=None):
    if self.stock_entry_type == "Manufacture":
        if len(self.items) > 0:
            print("Inside Function")
            for item in self.items:
                has_batch_no_checked = frappe.db.get_value("Item", item.item_code, 'has_batch_no')
                automatic_create_batch = frappe.db.get_value("Item", item.item_code, 'create_new_batch')
                is_finished_item = item.is_finished_item
                if has_batch_no_checked == 1 and automatic_create_batch == 0 and is_finished_item == 1: 
                    # if item.use_serial_batch_fields == 0 and item.batch_no == None:
                        # Check If Batch No Exists 
                        batch_no = check_batch_no_exist(item.item_code, has_batch_no_checked, self.posting_date)
                        if batch_no!=None:
                            item.use_serial_batch_fields = 1
                            item.batch_no = batch_no
                            frappe.msgprint(_('Item {0} existing  batch {1} is added').format(item.item_code,item.batch_no),alert=True, indicator="orange")
                        else:
                            # Generate Batch No and Set 
                            batch_no = generate_batch_no(item.item_code, has_batch_no_checked, self.posting_date)
                            if batch_no != None:
                                item.use_serial_batch_fields = 1
                                item.batch_no = batch_no
                                frappe.msgprint(_('Item {0} new batch {1} is added').format(item.item_code,item.batch_no),alert=True,indicator="green")


def check_batch_no_exist(item_code, batch_no_checked, posting_date):
    batch_name = None
    if batch_no_checked == 1:
        batch_prefix = frappe.db.get_value("Item", item_code, "custom_batch_prefix")
        expected_batch_name = "{0}-{1}".format(batch_prefix, frappe.utils.getdate(posting_date).strftime("%Y%m%d"))

    batches_found = frappe.db.get_list("Batch", {
                        "item" : item_code,
                        # "reference_doctype" : "Stock Entry",
                        "name" : expected_batch_name
                    },
                    pluck = "name")

    if len(batches_found) > 0:
        print(batches_found)
        batch_name = batches_found[0]
    return batch_name
    
def generate_batch_no(item_code, batch_no_checked, posting_date):
    def make_batch(item_code, posting_date, batch_id):
        if frappe.db.get_value("Item", item_code, "has_batch_no")  == 1:
            doc = frappe.new_doc("Batch")   
            doc.batch_id = batch_id
            doc.item = item_code
            doc.manufacturing_date = posting_date
            doc.stock_uom = frappe.db.get_value('Item', item_code, 'stock_uom')
            # doc.reference_doctype = "Stock Entry"

            doc.insert(ignore_permissions = True)

            return doc.name
        
    generated_batch_no = None
    if batch_no_checked == 1:   
        batch_prefix = frappe.db.get_value("Item", item_code, "custom_batch_prefix")
        batch_suffix = frappe.utils.getdate(posting_date).strftime("%Y%m%d")
        batch_id = "{0}-{1}".format(batch_prefix, batch_suffix)

        generated_batch_no = make_batch(item_code, posting_date, batch_id)
        return generated_batch_no


def fetch_ot_weekly_off_public_holidays_in_salary_slip(self, method=None):
    # First Check In Employee Holiday List If Not Then Take Company
    holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")
    if holiday_list == None:
        holiday_list = frappe.db.get_value("Company", self.company, "default_holiday_list")
        if holiday_list == None:
            frappe.throw("Please Assign Holiday List To Either Employee or Company.")
    
    weekly_off = frappe.db.get_all(
        doctype = "Holiday",
        parent_doctype="Holiday List",
        filters={"parent":holiday_list,"weekly_off":1, "holiday_date":['between', [self.start_date, self.end_date]]},
        fields = [{'COUNT': 'holiday_date', 'as': 'wo'}],
        debug = 1
    )
    
    public_holidays = frappe.db.get_all(
        doctype = "Holiday",
        parent_doctype="Holiday List",
        filters={"parent":holiday_list,"weekly_off":0, "holiday_date":['between', [self.start_date, self.end_date]]},
        fields = [{'COUNT': 'holiday_date', 'as': 'ph'}],
        debug = 1
    )

    ot_days = frappe.db.sql(
        '''
        SELECT overtime_days FROM `tabVbond Overtime` WHERE docstatus = 1 AND employee = '{0}' AND payroll_date BETWEEN '{1}' AND '{2}';
        '''.format(self.employee, self.start_date, self.end_date)
        , as_dict = 1, debug = 1
    )
    self.custom_overtime_days = ot_days[0].overtime_days if len(ot_days) > 0 else 0
    self.custom_weekly_off = weekly_off[0].wo if len(weekly_off) > 0 else 0
    self.custom_public_holidays = public_holidays[0].ph if len(public_holidays)>0 else 0
    self.save(ignore_permissions=True)

def cancel_overtime_on_cancel_of_additional_salary(self, method=None):
    if self.custom_overtime_ref != None:
        overtime_doc = frappe.get_doc("Vbond Overtime", self.custom_overtime_ref)
        if overtime_doc:
            overtime_doc.cancel()
            frappe.msgprint("Overtime Doctype For This Additional Salary Is Cancelled.", alert=True)
    else:
        overtime_doc_list = frappe.db.get_all(
            "Vbond Overtime",
            filters = {
                "payroll_date": self.payroll_date,
                "employee": self.employee,
                "docstatus": 1
            },
            pluck = "name",
            limit = 1,
            order_by = "payroll_date DESC"
        )
        if overtime_doc_list != [] and len(overtime_doc_list) > 0:
            overtime_doc = frappe.get_doc("Vbond Overtime", overtime_doc_list[0])
            if overtime_doc:
                overtime_doc.cancel()
                frappe.msgprint("Overtime Doctype For This Additional Salary Is Cancelled.", alert=True)
    
            
@frappe.whitelist()
def po_data(item_code):
    filters = {
        'from_date': frappe.utils.add_months(frappe.utils.today(), -3),
        "to_date" :frappe.utils.today(),
        "company" :erpnext.get_default_company(),
        "item_code": item_code
	}
    data = execute(filters)
    
    res = []
    if len(data) > 0:
        if data[1]:
            res = [data[1][0]]
        else:
            res = []
        
        for d in data[1]:
            isPresent = False
            for r in res:
                if res != [] and d['supplier_name'] == r['supplier_name']:
                    isPresent = True
            if isPresent == False:
                res.append(d)
            
    return res


def generate_and_set_batch_no_in_purchase_receipt(self,method=None):
    if len(self.items) > 0:
        for item in self.items:
            has_batch_no_checked = frappe.db.get_value("Item", item.item_code, 'has_batch_no')
            automatic_create_batch = frappe.db.get_value("Item", item.item_code, 'create_new_batch')
            if has_batch_no_checked == 1 and automatic_create_batch == 0: 
                batch_no = check_valid_batch_no_exist(item.item_code, has_batch_no_checked, self.posting_date, self.doctype)
                if batch_no!=None:
                    item.use_serial_batch_fields = 1
                    item.batch_no = batch_no
                    frappe.msgprint(_('For Item {0} existing  batch {1} is added').format(item.item_code,item.batch_no),alert=True, indicator="orange")
                else:
                    batch_no = generate_valid_batch_no(item.item_code, has_batch_no_checked, self.posting_date, self.doctype)
                    if batch_no != None:
                        item.use_serial_batch_fields = 1
                        item.batch_no = batch_no
                        frappe.msgprint(_('For Item {0} new batch {1} is added').format(item.item_code,item.batch_no),alert=True,indicator="green")

def check_valid_batch_no_exist(item_code, batch_no_checked, posting_date, doctype):
    batch_name = None
    if batch_no_checked == 1:
        batch_prefix = frappe.db.get_value("Item", item_code, "custom_batch_prefix")
        expected_batch_name = "PR-{0}-{1}".format(batch_prefix, frappe.utils.getdate(posting_date).strftime("%Y%m%d"))
    batches_found = frappe.db.get_list(
                        "Batch", 
                        {
                            "item" : item_code,
                            # "reference_doctype" : doctype, #### This is commented due to Duplicate Entry issue .... Ticket reference : 1341 - Purchase Receipt Batch Prefix Issue
                            "name" : expected_batch_name
                        },
                        pluck = "name"
                    )
    if len(batches_found) > 0:
        print(batches_found)
        batch_name = batches_found[0]
    return batch_name

def generate_valid_batch_no(item_code, batch_no_checked, posting_date, doctype):
    def make_batch(item_code, posting_date, batch_id, doctype):
        if frappe.db.get_value("Item", item_code, "has_batch_no")  == 1:
            doc = frappe.new_doc("Batch")   
            doc.batch_id = batch_id
            doc.item = item_code
            doc.manufacturing_date = posting_date
            doc.stock_uom = frappe.db.get_value('Item', item_code, 'stock_uom')
            # doc.reference_doctype = doctype
            doc.insert(ignore_permissions = True)
            return doc.name
        
    generated_batch_no = None
    if batch_no_checked == 1:   
        batch_prefix = frappe.db.get_value("Item", item_code, "custom_batch_prefix")
        batch_suffix = frappe.utils.getdate(posting_date).strftime("%Y%m%d")
        batch_id = "PR-{0}-{1}".format(batch_prefix, batch_suffix)
        generated_batch_no = make_batch(item_code, posting_date, batch_id, doctype)
        return generated_batch_no
    

def get_discount_percentage_from_slabs(slabs, value, from_fieldname, to_fieldname):
    value = flt(value)
    for slab in slabs:
        from_value = flt(slab.get(from_fieldname))
        to_value = flt(slab.get(to_fieldname))
        if value > from_value and (to_value == 0 or value <= to_value):
            return flt(slab.discount_percentage)
    return 0


def get_discount_percentage_based_on_range(state, tonnage, total_amount, is_based_on_weight):
    vbond_settings_doc = frappe.get_doc("Vbond Settings")
    tonnage = flt(tonnage)
    total_amount = flt(total_amount)

    if len(vbond_settings_doc.weight_discount_slabs_details_at)==0:
        frappe.throw(_("Please Set Weight Discount Slabs Details for Telangana & Andhra Pradesh in {0}".format(get_link_to_form("Vbond Settings","Vbond Settings"))))

    if len(vbond_settings_doc.weight_discount_slabs_details_ot)==0:
        frappe.throw(_("Please Set Weight Discount Slabs Details for Other States in {0}".format(get_link_to_form("Vbond Settings","Vbond Settings"))))

    if len(vbond_settings_doc.value_discount_slabs_details)==0:
        frappe.throw(_("Please Set Value Discount Slabs Details in {0}".format(get_link_to_form("Vbond Settings","Vbond Settings"))))

    if is_based_on_weight:
        slabs = (
            vbond_settings_doc.weight_discount_slabs_details_at
            if state in ["Telangana", "Andhra Pradesh"]
            else vbond_settings_doc.weight_discount_slabs_details_ot
        )
        return get_discount_percentage_from_slabs(slabs, tonnage, "from_mt", "to_mt")

    return get_discount_percentage_from_slabs(
        vbond_settings_doc.value_discount_slabs_details, total_amount, "from_amount", "to_amount"
    )


@frappe.whitelist()
def get_default_discount_template(company, discount_template=None):
    if not company:
        return {}

    if discount_template:
        template_company = frappe.get_cached_value("Discount Template VB", discount_template, "company")
        if template_company != company:
            return {}

    default_template = frappe.db.get_value(
        "Discount Template VB", {"default": 1, "company": company, "disable": 0}
    )
    if not default_template:
        frappe.msgprint(_("Default Discount template not found"),alert=True)

    return {
        "discount_template": default_template,
        "discount_template_details": get_discount_template_details(default_template),
    }


@frappe.whitelist()
def fetch_default_discount_template(self, method=None):
    if hasattr(self,"is_return"):
        if self.is_return == 0:
            calculate_discount = True
        else :
            calculate_discount = False
    else :
        calculate_discount = True

    if calculate_discount == True:
        if self.get("custom_discount_template_details"):
            if self.is_new() or not self.has_value_changed("custom_apply_vbond_discount"):
                return

        if not self.get("company"):
            return

        result = get_default_discount_template(self.company, self.get("custom_discount_template"))
        if not result:
            return

        if result.get("discount_template"):
            self.custom_discount_template = result.get("discount_template")

        if result.get("discount_template_details"):
            self.set("custom_discount_template_details", result.get("discount_template_details"))


@frappe.whitelist()
def get_discount_template_details(discount_template):
    if not discount_template:
        return []

    template = frappe.get_doc("Discount Template VB", discount_template)
  
    details = []
    for row in template.get("discount_template_details"):
        row = row.as_dict()
        new_row = {}
        new_row["auto_calculate"] = row.auto_calculate
        new_row["apply_on"] = row.apply_on
        new_row["type_of_discount"] = row.type_of_discount
        new_row["discount_percentage_vb"] = row.discount_percentage_vb
        details.append(new_row)

    return details


@frappe.whitelist()
def fetch_trade_and_product_discount_percentage_from_settings(self, method=None):
    if hasattr(self,"is_return"):
        if self.is_return == 0:
            calculate_discount = True
        else :
            calculate_discount = False
    else :
        calculate_discount = True

    if self.get("custom_apply_vbond_discount") != 1:
        for row in self.items:
            row.custom_trade_discount_percentage = 0
            row.custom_product_discount_percentage = 0
            row.discount_percentage = 0
            row.discount_amount = 0
            if row.price_list_rate:
                row.rate = row.price_list_rate
        return

    if calculate_discount == True:
        if len(self.items) == 0:
            return

        for row in self.items:
            ### set discount percentages and calculate discount amount first time only, if user changed the discount percentage then calculations will be based on it
            trade_discount_percentage = row.custom_trade_discount_percentage
            product_discount_percentage = row.custom_product_discount_percentage
            total_discount_percentage = trade_discount_percentage + (
                (1 - trade_discount_percentage / 100) * product_discount_percentage
            )
            row.discount_percentage = total_discount_percentage
            if row.price_list_rate:
                row.discount_amount = flt(
                    row.price_list_rate * total_discount_percentage / 100, row.precision("discount_amount")
                )
                row.rate = flt(row.price_list_rate - row.discount_amount, row.precision("rate"))
        self.calculate_taxes_and_totals()


@frappe.whitelist()
def calculate_discount_from_template(self, method=None):
    if hasattr(self,"is_return"):
        if self.is_return == 0:
            calculate_discount = True
        else :
            calculate_discount = False
    else :
        calculate_discount = True


    if calculate_discount == True:
        
        if not self.get("custom_discount_template_details"):
            return

        if self.get("custom_apply_vbond_discount") != 1:
            for row in self.custom_discount_template_details:
                row.discount_percentage_vb = 0
                row.discount_amount_vb = 0
                row.amount_after_discount = 0
            self.discount_amount = 0
            self.custom_insurance_percentage = 0
            self.custom_insurance_amount = 0
            return

        tonnage = (self.total_net_weight / 1000) or 0
        total_amount = self.total or 0
        previous_row_total = self.total or 0
        total_discount_amount = 0

        for row in self.custom_discount_template_details:
            if row.auto_calculate == 1:
                is_based_on_weight = 0
                fetch_from_settings = 0
                if row.type_of_discount:
                    is_based_on_weight = frappe.get_cached_value(
                        "Discount Type VB", row.type_of_discount, "is_based_on_weight"
                    )
                    fetch_from_settings = frappe.get_cached_value(
                        "Discount Type VB", row.type_of_discount, "fetch_from_settings"
                    )
                if fetch_from_settings == 1:
                    row.discount_percentage_vb = get_discount_percentage_based_on_range(
                        self.custom_state, tonnage, total_amount, is_based_on_weight
                    )

            base_amount = self.total if row.apply_on == "On Total" else previous_row_total
            row.discount_amount_vb = flt(
                base_amount * (row.discount_percentage_vb or 0) / 100, row.precision("discount_amount_vb")
            )
            row.amount_after_discount = flt(
                base_amount - row.discount_amount_vb, row.precision("amount_after_discount")
            )

            previous_row_total = row.amount_after_discount
            total_discount_amount += row.discount_amount_vb

        insurance_percentage = flt(frappe.db.get_single_value("Vbond Settings", "insurance"))
        if self.custom_allow_overwrite_insurance_precentage==1:
            insurance_percentage = self.custom_insurance_percentage
        else:
            self.custom_insurance_percentage = insurance_percentage
        last_row_amount_after_discount = self.custom_discount_template_details[-1].amount_after_discount
        insurance_amount = flt(
            last_row_amount_after_discount * insurance_percentage / 100, self.precision("discount_amount")
        )
    
        self.custom_insurance_amount = insurance_amount

        self.discount_amount = flt(total_discount_amount - insurance_amount, self.precision("discount_amount"))

@frappe.whitelist()
def fetch_trade_and_product_discount_from_settings(row):
    # row = json.loads(row)
    row = frappe._dict(json.loads(row))
    trade_discount_percentage = flt(frappe.db.get_single_value("Vbond Settings", "trade_discount_percentage"))
    if trade_discount_percentage == 0:
        frappe.throw(_("Please set Trade Discount Percentage in {0}").format(get_link_to_form("Vbond Settings", "Vbond Settings")))

    product_discount_percentage = flt(frappe.db.get_single_value("Vbond Settings", "product_discount_percentage"))
    if product_discount_percentage == 0:
        frappe.throw(_("Please set Product Discount Percentage in {0}").format(get_link_to_form("Vbond Settings", "Vbond Settings")))

    return {
        "trade_discount_percentage": trade_discount_percentage,
        "product_discount_percentage": product_discount_percentage
    }