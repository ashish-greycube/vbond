// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Delivery Note", {
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

    custom_transport_destination: function(frm) {
        let destination = frm.doc.custom_transport_destination
        frappe.db.get_value(
            doctype = "Destination VB",
            filters = {
                'name' : destination,
            },
            fieldname = ['kms']
        ).then(r => {
            let kms = r.message.kms
            frm.set_value('custom_destination_distance', kms)
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