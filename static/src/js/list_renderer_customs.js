/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { actionService } from "@web/webclient/actions/action_service";

var ActionService = actionService;

patch(ListRenderer.prototype, "list_renderer_customs", {
    setup() {
        //debugger;       
        this._super.apply(this, arguments);        
        owl.onMounted(this.autofocusForRadioCells);                   
    },

    syncCheckBoxes(record, subject_id, list){
        list.forEach(function(row){                                           
            if(row.id != record.id && subject_id == row.data.subject_id[0]){   
                row.selected = !record.selected;
            }                                
        });
    },

    onClickCapture(record, ev){        
        if(ev.target.type == "checkbox"){            
            switch(record.resModel){
                case "ims.subject_view":                     
                    var subject_id = record.data.subject_id[0];                     
                    if(this.props.list.groups == undefined){                        
                        this.syncCheckBoxes(record, subject_id, this.props.list.records);
                    }
                    else{     
                        var self = this;                                                  
                        this.props.list.groups.forEach(function(group){
                            self.syncCheckBoxes(record, subject_id, group.list.records);
                        });
                    }
                    break;
            }   
        }
        else{
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
                        context: record.context,
                    });
                    break;

                case "ims.subject_view":
                    ev.preventDefault();
                    ev.stopPropagation();                                

                    var controller = this.env.services.action.currentController;
                    var am = ActionService.start(this.env);                     
                    
                    am.doAction({                        
                        type: 'ir.actions.act_window',
                        res_model: 'ims.subject',                
                        res_id: record.data.subject_id[0],
                        views: [[false, "form"]],                                
                        target: 'current', //with 'new' the form opens as a modal window.
                        context: {
                            'subject_view_controller' : {
                                'jsId' : controller.jsId,
                                'name' : controller.displayName,
                            }
                        },
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