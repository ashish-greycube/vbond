import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrate():
    custom_fields = {
      "Delivery Note" : [
        # Transport Data Fields 
        {
          'fieldname' : 'custom_destination_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'set_target_warehouse',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_state',
          'fieldtype' : 'Link',
          'label' : 'State',
          'insert_after' : 'custom_destination_section',
          'options' : 'State VB',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_transport_destination',
          'fieldtype' : 'Link',
          'label' : 'Destination',
          'insert_after' : 'custom_state',
          'options' : 'Destination VB',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_dest_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_transport_destination',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_vehicle_type',
          'fieldtype' : 'Select',
          'label' : 'Vehicle Type',
          'insert_after' : 'custom_dest_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'options' : 'Hired\nDedicated / Company Owned\nTPL(Third Party Logistics)'
        },
        {
          'fieldname' : 'custom_vehicle_number',
          'fieldtype' : 'Link',
          'label' : 'Vehicle No (Dedicated / Company Owned)',
          'insert_after' : 'custom_vehicle_type',
          'options' : 'Vehicle',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"',
          'mandatory_depends_on' : 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_hired_vehicle_number',
          'fieldtype' : 'Data',
          'label' : 'Vehicle No (Hired / Third Party Logistics)',
          'insert_after' : 'custom_vehicle_number',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Hired" || doc.custom_vehicle_type=="TPL(Third Party Logistics)"'
        },
        {
          'fieldname' : 'custom_transport_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'items',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_destination_distance',
          'fieldtype' : 'Float',
          'label' : 'Destination Distance',
          'insert_after' : 'custom_transport_section',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'mandatory_depends_on' : 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_transport_rate_per_km',
          'fieldtype' : 'Float',
          'label' : 'Transport Rate/KM',
          'insert_after' : 'custom_destination_distance',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_transport_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_transport_rate_per_km',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_transport_cost',
          'fieldtype' : 'Currency',
          'label' : 'Transport Cost',
          'insert_after' : 'custom_transport_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_basic_amount',
          'fieldtype' : 'Currency',
          'label' : 'Basic Amount',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'insert_after' : 'net_total'
        },
        {
          'fieldname' : 'custom_total_tonnage',
          'fieldtype' : 'Float',
          'label' : 'Total Tonnage (MT)',
          'insert_after' : 'total_net_weight',
          'is_custom_field' : 1,
          'is_system_generated' : 0,  
          "read_only": 1,
        },


        # Logistics Report Fields
        {
          'fieldname' : 'custom_driver_no',
          'fieldtype' : 'Phone',
          'label' : 'Driver No',
          'insert_after' : 'driver',
          'is_custom_field' : 1,
          'is_system_generated' : 0
        },
        {
          'fieldname' : 'custom_datetime_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'ignore_pricing_rule',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_alloc_datetime',
          'fieldtype' : 'Datetime',
          'label' : 'Alloc Date & Time',
          'insert_after' : 'custom_datetime_section',
          'is_custom_field' : 1,
          'is_system_generated' : 0
        },
        {
          'fieldname' : 'custom_dispatch_datetime',
          'fieldtype' : 'Datetime',
          'label' : 'Dispatch Date & Time',
          'insert_after' : 'custom_alloc_datetime',
          'is_custom_field' : 1,
          'is_system_generated' : 0
        },
        {
          'fieldname' : 'custom_delivered_datetime',
          'fieldtype' : 'Datetime',
          'label' : 'POD Time',
          'insert_after' : 'custom_dispatch_datetime',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'allow_on_submit' : 1,
        },
        {
          'fieldname' : 'custom_pod_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_delivered_datetime',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_pod_status',
          'fieldtype' : 'Select',
          'label' : 'POD Status',
          'insert_after' : 'custom_pod_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'options' : '\nIssue\nNo Issue',
          'allow_on_submit' : 1,
        },
        {
          'fieldname' : 'custom_pod_remarks',
          'fieldtype' : 'Small Text',
          'label' : 'POD Remarks',
          'insert_after' : 'custom_pod_status',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'mandatory_depends_on' : 'eval:doc.custom_pod_status == "Issue"',
          'allow_on_submit' : 1,
        },
        {
          'fieldname' : 'custom_action_plan',
          'fieldtype' : 'Small Text',
          'label' : 'Action Plan',
          'insert_after' : 'custom_pod_remarks',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on' : 'eval:doc.custom_pod_status == "Issue"',
          'allow_on_submit' : 1,
        },
      ],

      "Sales Order" : [
        # Transport Data Fields
        {
          'fieldname' : 'custom_destination_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'reserve_stock',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_state',
          'fieldtype' : 'Link',
          'label' : 'State',
          'insert_after' : 'custom_destination_section',
          'options' : 'State VB',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_transport_destination',
          'fieldtype' : 'Link',
          'label' : 'Destination',
          'insert_after' : 'custom_state',
          'options' : 'Destination VB',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_dest_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_transport_destination',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_vehicle_type',
          'fieldtype' : 'Select',
          'label' : 'Vehicle Type',
          'insert_after' : 'custom_dest_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'options' : 'Hired\nDedicated / Company Owned\nTPL(Third Party Logistics)'
        },
        {
          'fieldname' : 'custom_vehicle_number',
          'fieldtype' : 'Link',
          'label' : 'Vehicle No (Dedicated / Company Owned)',
          'insert_after' : 'custom_vehicle_type',
          'options' : 'Vehicle',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"',
          'mandatory_depends_on' : 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_hired_vehicle_number',
          'fieldtype' : 'Data',
          'label' : 'Vehicle No (Hired / Third Party Logistics)',
          'insert_after' : 'custom_vehicle_number',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Hired" || doc.custom_vehicle_type=="TPL(Third Party Logistics)"'
        },
        {
          'fieldname' : 'custom_transport_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'items',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_destination_distance',
          'fieldtype' : 'Float',
          'label' : 'Destination Distance',
          'insert_after' : 'custom_transport_section',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'mandatory_depends_on' : 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_transport_rate_per_km',
          'fieldtype' : 'Float',
          'label' : 'Transport Rate/KM',
          'insert_after' : 'custom_destination_distance',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_transport_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_transport_rate_per_km',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_transport_cost',
          'fieldtype' : 'Currency',
          'label' : 'Transport Cost',
          'insert_after' : 'custom_transport_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_total_tonnage',
          'fieldtype' : 'Float',
          'label' : 'Total Tonnage (MT)',
          'insert_after' : 'total_net_weight',
          'is_custom_field' : 1,
          'is_system_generated' : 0,  
          "read_only": 1,
        },

        # Logistics Report Fields
        {
          'fieldname' : 'custom_delivery_time',
          'fieldtype' : 'Time',
          'label' : 'Delivery Time',
          'insert_after' : 'delivery_date',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'allow_on_submit' : 1
        },
        {
          'fieldname' : 'custom_vehicle_req_datetime',
          'fieldtype' : 'Datetime',
          'label' : 'Vehicle Request Date & Time',
          'insert_after' : 'custom_delivery_time',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
      ], 

      "Sales Invoice" : [
        {
          'fieldname' : 'custom_destination_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'set_target_warehouse',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_state',
          'fieldtype' : 'Link',
          'label' : 'State',
          'insert_after' : 'custom_destination_section',
          'options' : 'State VB',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_transport_destination',
          'fieldtype' : 'Link',
          'label' : 'Destination',
          'insert_after' : 'custom_state',
          'options' : 'Destination VB',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_dest_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_transport_destination',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_vehicle_type',
          'fieldtype' : 'Select',
          'label' : 'Vehicle Type',
          'insert_after' : 'custom_dest_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'options' : 'Hired\nDedicated / Company Owned\nTPL(Third Party Logistics)'
        },
        {
          'fieldname' : 'custom_vehicle_number',
          'fieldtype' : 'Link',
          'label' : 'Vehicle No (Dedicated / Company Owned)',
          'insert_after' : 'custom_vehicle_type',
          'options' : 'Vehicle',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"',
          'mandatory_depends_on' : 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_hired_vehicle_number',
          'fieldtype' : 'Data',
          'label' : 'Vehicle No (Hired / Third Party Logistics)',
          'insert_after' : 'custom_vehicle_number',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Hired" || doc.custom_vehicle_type=="TPL(Third Party Logistics)"'
        },
        {
          'fieldname' : 'custom_transport_section',
          'fieldtype' : 'Section Break',
          'insert_after' : 'items',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_destination_distance',
          'fieldtype' : 'Float',
          'label' : 'Destination Distance',
          'insert_after' : 'custom_transport_section',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'mandatory_depends_on' : 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_transport_rate_per_km',
          'fieldtype' : 'Float',
          'label' : 'Transport Rate/KM',
          'insert_after' : 'custom_destination_distance',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'depends_on': 'eval:doc.custom_vehicle_type=="Dedicated / Company Owned"'
        },
        {
          'fieldname' : 'custom_transport_column_break',
          'fieldtype' : 'Column Break',
          'insert_after' : 'custom_transport_rate_per_km',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_transport_cost',
          'fieldtype' : 'Currency',
          'label' : 'Transport Cost',
          'insert_after' : 'custom_transport_column_break',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
        },
        {
          'fieldname' : 'custom_basic_amount',
          'fieldtype' : 'Currency',
          'label' : 'Basic Amount',
          'is_custom_field' : 1,
          'is_system_generated' : 0,
          'insert_after' : 'net_total'
        },
        {
          'fieldname' : 'custom_total_tonnage',
          'fieldtype' : 'Float',
          'label' : 'Total Tonnage (MT)',
          'insert_after' : 'total_net_weight',
          'is_custom_field' : 1,
          'is_system_generated' : 0,  
          "read_only": 1,
        },
      ],

      "Vehicle" : [
          {
              'fieldname' : 'cutom_vehicle_type',
              'fieldtype' : 'Select',
              'label' : 'Vehicle Type',
              'insert_after' : 'location',
              'is_custom_field': 1,
              'is_system_generated': 0,
              'options': '\nDedicated / Company Owned\nHired\nTPL(Third Party Logistics)'
          },
          {
              'fieldname' : 'custom_rate_per_km',
              'fieldtype' : 'Float',
              'label' : 'Rate Per KM',
              'insert_after' : 'employee',
              'is_custom_field': 1,
              'is_system_generated': 0,
          } 
      ],

      "Vehicle Log" : [
          {
            'fieldname' : 'custom_sales_order',
            'fieldtype' : 'Link',
            'label' : 'Sales Order',
            'options' : 'Sales Order',
            'insert_after' : 'make',
            'is_custom_field' : 1,
            'is_system_generated' : 0,
          },
          {
            'fieldname' : 'custom_arrival_time_date',
            'fieldtype' : 'Datetime',
            'label' : 'Arrival Date & Time',
            'insert_after' : 'column_break_12',
            'is_custom_field' : 1,
            'is_system_generated' : 0,
          },
          {
            'fieldname' : 'custom_vehicle_type',
            'fieldtype' : 'Select',
            'label' : 'Vehicle Type',
            'insert_after' : 'license_plate',
            'is_custom_field' : 1,
            'is_system_generated' : 0,
            'options' : '\nHired\nDedicated / Company Owned\nTPL(Third Party Logistics)',
            'fetch_from' : "license_plate.cutom_vehicle_type"
          },
          {
            'fieldname' : 'custom_trip_km',
            'fieldtype' : 'Float',
            'label' : 'Trip KM',
            'insert_after' : 'odometer',
            'is_custom_field' : 1,
            'is_system_generated' : 0,
          }
      ]
    }



    print("Adding Custom Fields In SO, SI and DN.....")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)