/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { actionService } from "@web/webclient/actions/action_service";
// import { jsonrpc } from "@web/core/network/rpc_service";

var ActionService = actionService;

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        //owl.onMounted(this.autofocusForRadioCells);                   
    },

    // getModelId(model, xml_id){
    //     debugger;
    //     jsonrpc.query({
    //         model: model,
    //         method: 'search_read',                        
    //         args: [[], ['xml_id', 'name']],
    //         //TODO: domain not working, try to get the main model in order to avoid looping in the result!
    //         //args: [['xml_id', '=', 'ims.action_subject_tree'], ['xml_id', 'name', 'context']],                         
    //     }).then(function (data) { 
    //         data = data.filter(function(item){
    //             return item.xml_id == xml_id;
    //         });
    //         debugger;
    //     }); 
    // },

    // syncCheckBoxes(record, subject_id, list){
    //     list.forEach(function(row){                                           
    //         if(row.id != record.id && subject_id == row.data.subject_id[0]){   
    //             row.selected = !record.selected;
    //         }                                
    //     });
    // },

    onClickCapture(record, ev){ 
        var am = ActionService.start(this.env);

        if(ev.target.type == "checkbox"){               
            // switch(record.resModel){
            //     case "ims.subject_view":                     
            //         var subject_id = record.data.subject_id[0];                     
            //         if(this.props.list.groups == undefined){                        
            //             this.syncCheckBoxes(record, subject_id, this.props.list.records);
            //         }
            //         else{     
            //             var self = this;                                                  
            //             this.props.list.groups.forEach(function(group){
            //                 self.syncCheckBoxes(record, subject_id, group.list.records);
            //             });
            //         }
            //         break;
            // }   
        }
        else{             
            switch(record.resModel){                
                case "ims.enrollment_view":
                    ev.preventDefault();
                    ev.stopPropagation();            
                 
                //     am.doAction({
                //         name: 'Open: Students', //to fit with the other regular student's tab
                //         type: 'ir.actions.act_window',
                //         res_model: 'res.partner',                
                //         res_id: record.data.student_id[0],
                //         views: [[false, "form"]],                                
                //         target: 'new', //with 'current' the form opens in fullscreen (not modal).
                //         context: record.context,
                //     });
                    debugger;
                    //this.env.searchModel.orm.call("ims.enrollment_view", "open_form_student", []);
                    // TODO: try to call a server method to get the corrent view ID or to call the form:
                    //  https://www.odoo.com/documentation/18.0/es/developer/reference/frontend/javascript_reference.html#talking-to-the-server
                    this.env.model.orm.call("ims.enrollment_view", "open_form_student", []);
                    //this.getModelId("ir.ui.view", "base.view_partner_form");        
                    break;

                case "ims.subject_view":
                    ev.preventDefault();
                    ev.stopPropagation();                                
                                    
                    am.doAction({                        
                        type: 'ir.actions.act_window',
                        res_model: 'ims.subject',                
                        res_id: record.data.subject_id[0],
                        views: [[false, "form"]],
                        target: 'current', //with 'new' the form opens as a modal window.   
                        context: record.context,                    
                        // context: {
                        //     'subject_view_list' : true
                        // },
                    });
                    break;
            }    
        }    
    },       

    // autofocusForRadioCells(){                
    //     var self = this;
    //     // TODO: should be reloaded on session change...

    //     // NOTE: This is fired by onMounted and all the DOM is ready and $(".o_field_cell.o_radio_cell").length != 0 BUT when saving, must be
    //     // fired again and $(".o_field_cell.o_radio_cell").length == 0 so, a timer is needed. 
    //     var intervalID = setInterval(function(){
    //         if($(".o_field_cell.o_radio_cell").length != 0){                                
    //             clearInterval(intervalID);                
                
    //             $(".o_form_button_save").off('click').on("click", self.autofocusForRadioCells);

    //             $(".o_field_cell.o_radio_cell").off('mouseover').on("mouseover", function(){
    //                 $(this).mouseover(function() {                                    
    //                     $(this).click();
    //                 });
        
    //                 $(this).mouseout(function() {
    //                     $(".o_horizontal_separator").first().click();
    //                 });
    //             }); 
    //         } 
    //     }, 100);                               
    // },
});