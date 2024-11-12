/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

var _intervalID = null;

// TODO: check transient_enrollment_click in order to try to capture the "hover" event natively

patch(FormController.prototype, "radiobutton_autofocus", {
    setup(){    
        this._super.apply();
        this.action = useService("action");    

        if(this.props.resModel == "ims.attendance_session"){
            start_poll();    
        }
    }     
});

function start_poll(){
    _intervalID = setInterval(poll, 100);
}

function poll(){
    if($(".o_field_cell.o_radio_cell").length != 0){
        clearInterval(_intervalID);        
        
        $(".o_form_button_save").off('click').on("click", start_poll());
        autofocusForAttendanceStatus();
    } 
}

function autofocusForAttendanceStatus(){
    $(".o_field_cell.o_radio_cell").on("mouseover", function(){
        $(this).mouseover(function() {                                    
            $(this).click();
        });

        $(this).mouseout(function() {
            $(".o_horizontal_separator").first().click();
        });
    });                        
} 
