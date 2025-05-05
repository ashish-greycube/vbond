import frappe

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
    if state in ['AP', 'TN', 'KA'] and weight > 0.0 and weight <= 8.0:
        mt_weight = "6_8_mt"
    
    elif state in ['TN', 'KA'] and weight > 12.0 and weight <= 16.0:
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

    elif vehicle_type == "Hired":
        state = self.custom_state
        destination = self.custom_transport_destination
        kg_weight = self.total_net_weight

        metric_weight = (kg_weight / 1000)
        mt_weight_range = get_mt_weight_range(metric_weight, state)
        
        if state and destination != None:
            transport_cost, distance = frappe.db.get_value(
                doctype = "Vbond Final Rate Card",
                filters = {
                    'destination' : destination,
                    'state' : state
                },
                fieldname = [mt_weight_range, 'kms',]
            )
          
            self.custom_destination_distance = distance
            self.custom_transport_cost = transport_cost

            # Moving Vehicle Number From Details To Transfer Section
            if self.doctype == "Delivery Note" or self.doctype == "Sales Invoice":
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