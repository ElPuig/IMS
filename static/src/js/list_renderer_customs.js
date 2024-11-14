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

    autofocusForRadioCells(){                
        var self = this;

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

        // console.log($(".o_field_cell.o_radio_cell").length);     
        // $(".o_field_cell.o_radio_cell").on("mouseover", function(){
        //     $(this).mouseover(function() {                                    
        //         $(this).click();
        //     });

        //     $(this).mouseout(function() {
        //         $(".o_horizontal_separator").first().click();
        //     });
        // });                        
    },

    // TODO: on saving, another event should be triggered but this not depends 
    // startPoll(){
    //     var self = this;
    //     var intervalID = setInterval(function(){
    //         if($(".o_field_cell.o_radio_cell").length != 0){
    //             clearInterval(intervalID);        
                
    //             $(".o_form_button_save").off('click').on("click", self.startPoll());
    //             self.autofocusForRadioCells();
    //         } 
    //     }, 100);
    // },
});