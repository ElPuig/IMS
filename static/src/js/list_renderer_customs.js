/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { actionService } from "@web/webclient/actions/action_service";

var ActionService = actionService;

patch(ListRenderer.prototype, "list_renderer_customs", {
    setup() {        
        this._super.apply(this, arguments);        
        owl.onMounted(this.autofocusForRadioCells);           
    },

    onClickCapture(record, ev){
        if(ev.target.type != "checkbox"){           
            switch(record.resModel){
                case "ims.enrollment_view":
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
                    break;

                case "ims.subject_view":
                    ev.preventDefault();
                    ev.stopPropagation();            
                    
                    var am = ActionService.start(this.env);                    
                    am.doAction({
                        //name: 'Open: Students', //to fit with the other regular student's tab
                        type: 'ir.actions.act_window',
                        res_model: 'ims.subject',                
                        res_id: record.data.subject_id[0],
                        views: [[false, "form"]],                                
                        target: 'current', //with 'new' the form opens as a modal window.
                        context: {},
                    });
                    break;
            }    
        }    
    },       

    autofocusForRadioCells(){                
        var self = this;
        // TODO: should be reloaded on session change...

        // NOTE: This is fired by onMounted and all the DOM is ready and $(".o_field_cell.o_radio_cell").length != 0 BUT when saving, must be
        // fired again and $(".o_field_cell.o_radio_cell").length == 0 so, a timer is needed. 
        var intervalID = setInterval(function(){
            if($(".o_field_cell.o_radio_cell").length != 0){                                
                clearInterval(intervalID);                
                
                $(".o_form_button_save").off('click').on("click", self.autofocusForRadioCells);

                $(".o_field_cell.o_radio_cell").off('mouseover').on("mouseover", function(){
                    $(this).mouseover(function() {                                    
                        $(this).click();
                    });
        
                    $(this).mouseout(function() {
                        $(".o_horizontal_separator").first().click();
                    });
                }); 
            } 
        }, 100);                               
    },
});