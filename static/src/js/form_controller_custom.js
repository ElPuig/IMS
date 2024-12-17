/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { FormView } from "@web/views/form/form_view";
import { useService } from "@web/core/utils/hooks";

patch(FormController.prototype, {
    setup(){
        this.orm = useService("orm");
        this.action = useService("action")
        super.setup();
    },
    async getViewData(xml_id){
        const data = await this.orm.searchRead("ir.ui.view", [["xml_id", "=", xml_id]], ["id", "xml_id", "name"]);
        var view = data.filter(function(item){
            //TODO: the domain is not working in the orm searchRead method... WHY?
            return item.xml_id == xml_id;
        })[0];
        return view;
    },
    _onButtonClicked(event) {
        console.log(event);
    },
    expandStudentForm(){
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            res_id: record.data.student_id[0],
            views: [[this.getViewData("view_contact_form").name, "form"]],   
            view_mode: "form",
            target: "current",
        });  
    }
});
