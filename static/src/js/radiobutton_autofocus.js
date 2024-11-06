/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

var _intervalID = null;

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

//A malas, si no consigo capturar el evento, puedo hacer un timer y cuando encuentre que ha cargado, lo aplique.

//Idea? https://www.cybrosys.com/blog/how-to-add-mouseover-popup-in-odoo-15-website
//      https://www.odoo.com/es_ES/forum/ayuda-1/how-can-i-receive-an-onclick-event-of-a-button-in-a-js-file-in-odoo-17-251948

/*
odoo.define('ims.radiobutton_autofocus', function (require) {
    "use strict";
    
    var core = require('web.core');
    var BasicController = require('web.BasicController');
    var FormController = require("web.FormController");
    
    
    FormController.include({
        events: {
            'change #any_field': '_onChange',
        },
        _onChange: function (event) {
            console.log('_onChange');
        },
        _onSave: function () {
            console.log('_onSave');
         },
    });

    $(document).ready(function() {  
        console.log('ready');
    });

});
*/

/*

 $(document).ready(function() {  
                        autofocusForAttendanceStatus();
                        
                        $(".o_form_button_save").on("click", function(){
                            /*
                                TODO: Ugly... Try to find an event or something... 
                                Check this out: https://www.odoo.com/es_ES/forum/ayuda-1/how-to-add-my-custom-javascript-code-into-form-view-page-225586
                                                https://stackoverflow.com/questions/52253493/how-to-perform-some-action-on-a-node-after-it-is-loaded-in-javascript-in-odoo
                                                https://www.odoo.com/es_ES/forum/ayuda-1/how-to-create-javascript-event-on-odoo16-214754
                                                https://www.odoo.com/es_ES/forum/ayuda-1/how-i-can-trigger-save-button-from-view-form-js-75550
                                                https://www.odoo.com/es_ES/forum/ayuda-1/how-to-add-special-javascript-code-to-a-from-view-261231
                            */
                           /*
                           
                                                setTimeout(function(){
                                                    autofocusForAttendanceStatus();
                                                }, 100);                            
                                            });
                           
                    
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
});

*/