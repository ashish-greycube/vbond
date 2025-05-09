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


    custom_transport_destination: function (frm) {
        let destination = frm.doc.custom_transport_destination
        frappe.db.get_value(
            doctype = "Destination VB",
            filters = {
                'name': destination,
            },
            fieldname = ['kms']
        ).then(r => {
            let kms = r.message.kms
            frm.set_value('custom_destination_distance', kms)
        })
    },


    custom_vehicle_number: function (frm) {
        let vehicle = frm.doc.custom_vehicle_number
        frappe.db.get_value(
            doctype = 'Vehicle',
            filters = {
                'name': vehicle
            },
            fieldname = ['custom_rate_per_km']
        ).then(r => {
            let rate = r.message.custom_rate_per_km
            frm.set_value('custom_transport_rate_per_km', rate)
        })
    }
    // refresh(frm) {
    //     if (frm.doc.custom_vehicle_type == "Dedicated") {
    //         frm.set_df_property('custom_vehicle_number', 'reqd', 1)
    //         frm.set_df_property('custom_hired_vehicle_number', 'hidden', 1)
    //         frm.set_df_property('custom_vehicle_number', 'hidden', 0)
    //     }
    //     else {
    //         frm.set_df_property('custom_vehicle_number', 'hidden', 1)
    //         frm.set_df_property('custom_hired_vehicle_number', 'hidden', 0)
    //     }
    // },

    // custom_vehicle_type(frm) {
    //     if (frm.doc.custom_vehicle_type == "Dedicated") {
    //         frm.set_df_property('custom_vehicle_number', 'reqd', 1)
    //         frm.set_df_property('custom_destination_distance', 'reqd', 1)
    //         frm.set_df_property('custom_hired_vehicle_number', 'hidden', 1)
    //         frm.set_df_property('custom_vehicle_number', 'hidden', 0)
    //     }
    //     else {
    //         frm.set_df_property('custom_vehicle_number', 'hidden', 1)
    //         frm.set_df_property('custom_hired_vehicle_number', 'hidden', 0)
    //         frm.set_df_property('custom_destination_distance', 'reqd', 0)
    //     }
    // },
});