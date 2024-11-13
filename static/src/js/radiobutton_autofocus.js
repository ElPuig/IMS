/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";
import { ListRenderer } from "@web/views/list/list_renderer";

var _intervalID = null;

// TODO: check transient_enrollment_click in order to try to capture the "hover" event natively
patch(ListRenderer.prototype, "radiobutton_autofocus_v2", {
    setup() {        
        this._super.apply(this, arguments);    
        debugger;                     
    },

    onRowTouchStart(record, ev){
        console.log("onRowTouchStart");     
    },   
    
    onRowTouchMove(record){
        console.log("onRowTouchMove");     
    },

    onRowTouchEnd(record){
        console.log("onRowTouchEnd");     
    },

    events: _.extend({}, ListRenderer.prototype.events, {
        'mouseover td.o_radio_cell': '_onMouseOver',                  
    }),

    _onMouseOver: function (event) {     
        console.log("_onMouseOver");       
    },  
});

// This code works, but not perfectly...
// patch(FormController.prototype, "radiobutton_autofocus", {
//     setup(){    
//         this._super.apply();
//         this.action = useService("action");    

//         if(this.props.resModel == "ims.attendance_session"){
//             start_poll();    
//         }
//     }     
// });

// function start_poll(){
//     _intervalID = setInterval(poll, 100);
// }

// function poll(){
//     if($(".o_field_cell.o_radio_cell").length != 0){
//         clearInterval(_intervalID);        
        
//         $(".o_form_button_save").off('click').on("click", start_poll());
//         autofocusForAttendanceStatus();
//     } 
// }

// function autofocusForAttendanceStatus(){
//     $(".o_field_cell.o_radio_cell").on("mouseover", function(){
//         $(this).mouseover(function() {                                    
//             $(this).click();
//         });

//         $(this).mouseout(function() {
//             $(".o_horizontal_separator").first().click();
//         });
//     });                        
// } 
