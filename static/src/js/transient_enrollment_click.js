/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { actionService } from "@web/webclient/actions/action_service";

var ActionService = actionService;
patch(ListRenderer.prototype, "transient_enrollment_click", {
    setup() {        
        this._super.apply(this, arguments);
    },

    onClickCapture(record, ev){        
        if(record.resModel == "ims.transient_enrollment"){
            ev.preventDefault();
            ev.stopPropagation();            

            var am = ActionService.start(this.env);                    
            am.doAction({
                name: 'Open: Students', //to fit with the other regular student's tab
                type: 'ir.actions.act_window',
                res_model: 'res.partner',                
                res_id: record.data.student_id[0],
                views: [[false, "form"]],                                
                target: 'new', //with 'current' the form opens in fullscreen (not modal).
                context: {},
            });                 
        }        
    },       
});