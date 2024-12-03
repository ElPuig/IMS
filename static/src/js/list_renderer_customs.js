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
        // TODO: for subject_view list --> Select all checkboxes with same subject_id or reload the list after removing
        //https://www.odoo.com/ro_RO/forum/suport-1/refresh-tree-view-after-closing-export-dialog-101044

        if(ev.target.type == "checkbox"){
            debugger;            
            //Firs loop:
            //  groups = this.props.list.groups
            //Second loop:
            //  records = groups[i].list.records
            //Third loop:
            //  data = records[i].data
            //      id --> datapoint_x --> tr[data-id="datapoint_x"] --> input[type="checkbox"] --> enable check

            //OLD:
            //  table = $(event.target).parent().parent().parent().parent()
            //  row = table.children(".o_data_row")[0]
            //  input = $(row).children(".o_list_record_selector")[0]
            //  input = $(input).children(".o-checkbox")[0]
            //  input = $(input).children(".form-check-input")[0]
            //  $(input).prop('checked', true);
        }

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