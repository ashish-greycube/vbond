frappe.ui.form.on("Purchase Order Item", {
    item_code(frm,cdt,cdn){
        code = locals[cdt][cdn].item_code
        frappe.call({
            method: "vbond.api.po_data",
            args : {
                "item_code" : code
            },
            callback: function(r) {
                if (r.message) {
                    let po_records = r.message;
                    let d_data = ""
                    for (let data of po_records){
                        s_name = data['supplier_name']
                        rate = data['rate']
                        d_data += 
                            `<tr>
                                <td style="border: 1px solid black; padding: 8px;">${s_name}</td>
                                <td style="border: 1px solid black; padding: 8px;">${rate}</td>
                            </tr>`
                    }
                    let msg = `<table style="border: 1px solid black; border-collapse: collapse; width: 100%;">
                                    <thead>
                                        <tr>
                                            <th style="border: 1px solid black; padding: 8px;">Supplier Name</th>
                                            <th style="border: 1px solid black; padding: 8px;">Rate</th>
                                        </tr>
                                    </thead>
                                    ${d_data}
                                </table>`; 
                    
                    if(d_data){
                        frappe.msgprint(msg,'Supplier History')
                    } else{
                        let today = frappe.datetime.nowdate()
                        let from_date = frappe.datetime.add_months(today, -3)
                        let company = frappe.defaults.get_user_default("Company") 
                        open_purchase_history = function() {
                            frappe.open_in_new_tab = true;
                            frappe.route_options = {
                                "company": company,
                                "from_date": from_date,
                                "to_date": today,
                                "item_code" :code
                            };
                            frappe.set_route("query-report", "Item-wise Purchase History");
                        };
                    
                        frappe.msgprint(`<P>There is No Data Available </P>
                                    <button style="border:1px solid black; border-radius: 5px;" onclick="open_purchase_history()">Show Report</button>`)
                    }                

                }

            }
        });
    }
})

