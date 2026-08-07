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

    onload_post_render(frm) {
        if (!frm.doc.is_return && frm.doc.docstatus == 0 && !frm.doc.custom_discount_template && !(frm.doc.custom_discount_template_details || []).length) {
            apply_default_discount_template(frm);
        }
    },

    company(frm) {
        if (!frm.doc.is_return && !frm.doc.custom_discount_template && !(frm.doc.custom_discount_template_details || []).length) {
            apply_default_discount_template(frm);
        }
    },

    custom_discount_template(frm) {
        console.log("from template")
        if (!frm.doc.custom_discount_template) {
            return;
        }
        frappe.call({
            method: "vbond.api.get_discount_template_details",
            args: {
                discount_template: frm.doc.custom_discount_template,
            },
            callback: function (r) {
                if (!r.exc) {
                    frm.set_value("custom_discount_template_details", r.message || []);
                }
            },
        });
    },


    after_save(frm) {
        // discount_amount is set server-side (before_validate), so ERPNext's
        // set_dynamic_labels() never re-evaluates net_total's visibility on save
        // (it's memoized on currency, which doesn't change). Force it to re-run.
        frm.cscript._last_currency = null;
        frm.cscript.set_dynamic_labels();
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

function apply_default_discount_template(frm) {
    console.log("from function------------------")
    if (!frm.doc.company) {
        return;
    }
    frappe.call({
        method: "vbond.api.get_default_discount_template",
        args: {
            company: frm.doc.company,
            discount_template: frm.doc.custom_discount_template || "",
        },
        callback: function (r) {
            if (!r.exc && r.message) {
                if (r.message.discount_template) {
                    frm.doc.custom_discount_template = r.message.discount_template;
                }
                if (r.message.discount_template_details) {
                    frm.set_value("custom_discount_template_details", r.message.discount_template_details);
                }
            }
        },
    });
}