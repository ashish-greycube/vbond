// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
    setup(frm) {
        frm.set_query('custom_transport_destination', function () {
            if (frm.doc.custom_state) {
                return {
                    query: 'vbond.api.filter_destination',
                    filters: {
                        'state': frm.doc.custom_state
                    }
                }
            }
        })
    },

    refresh(frm) {
        if (frm.doc.custom_vehicle_type == "Dedicated") {
            frm.set_df_property('custom_vehicle_number', 'reqd', 1)
            frm.set_df_property('custom_hired_vehicle_number', 'hidden', 1)
            frm.set_df_property('custom_vehicle_number', 'hidden', 0)
        }
        else {
            frm.set_df_property('custom_vehicle_number', 'hidden', 1)
            frm.set_df_property('custom_hired_vehicle_number', 'hidden', 0)
        }
    },

    custom_vehicle_type(frm) {
        if (frm.doc.custom_vehicle_type == "Dedicated") {
            frm.set_df_property('custom_vehicle_number', 'reqd', 1)
            frm.set_df_property('custom_destination_distance', 'reqd', 1)
            frm.set_df_property('custom_hired_vehicle_number', 'hidden', 1)
            frm.set_df_property('custom_vehicle_number', 'hidden', 0)
        }
        else {
            frm.set_df_property('custom_vehicle_number', 'hidden', 1)
            frm.set_df_property('custom_hired_vehicle_number', 'hidden', 0)
            frm.set_df_property('custom_destination_distance', 'reqd', 0)
        }
    },
});