import frappe
from frappe import _
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
                if has_batch_no_checked == 1 and automatic_create_batch == 0: 
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
                        "reference_doctype" : "Stock Entry",
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
            doc.reference_doctype = "Stock Entry"

            doc.insert(ignore_permissions = True)

            return doc.name
        
    generated_batch_no = None
    if batch_no_checked == 1:   
        batch_prefix = frappe.db.get_value("Item", item_code, "custom_batch_prefix")
        batch_suffix = frappe.utils.getdate(posting_date).strftime("%Y%m%d")
        batch_id = "{0}-{1}".format(batch_prefix, batch_suffix)

        generated_batch_no = make_batch(item_code, posting_date, batch_id)
        return generated_batch_no
