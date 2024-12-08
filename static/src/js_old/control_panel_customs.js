/** @odoo-module **/
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { patch } from "@web/core/utils/patch";
import { actionService } from "@web/webclient/actions/action_service";

var rpc = require("web.rpc");
var ActionService = actionService;

patch(ControlPanel.prototype, "control_panel_customs", {
    setup() {        
        this._super.apply(this, arguments);            
        owl.onMounted(() => {                 
            //The "Subject" breadcrum dissapears when jumping to another models, just like when refreshig and jumped from model to model using a button...
            //TODO: try to avoid missing the breadcrums on refreshing after pushing a button (through python action).    
            var model = this.env.searchModel.resModel;        
            if (this.env.config.viewType == "form" && this.breadcrumbs.length == 1 && model.startsWith("ims.")){
                //Workaroung to add the missing level-1 breadcrum, should be properly fixed.                                 
                var br = $(this.root.el).find("ol.breadcrumb");
                var am = ActionService.start(this.env);                
                                
                if($(br).children("li").length == 1){                                                                           
                    this.prependToBreadcrums(am, model, br);                           
                }
                else if (this.env.searchModel.context["subject_view_list"] == true){
                    //TODO: onMounted only fires once, so the breadcrums is updated becasue the form is changing, but not the entire document (SPA).
                    // It's worthy to workaround this? I think is better to upgrade to Odoo 18 and try to change something else...
                }
            }            
        });
    },
    
    prependToBreadcrums(am, model, br){
        if(model == "ims.subject") model = "ims.subject_view";  //from "subject" form to "subject_view" list.                    
        
        rpc.query({
            model: 'ir.actions.act_window',
            method: 'search_read',                        
            args: [[], ['xml_id', 'name', 'context']],                        
            //TODO: domain not working, try to get the main model in order to avoid looping in the result!
            //args: [['xml_id', '=', 'ims.action_subject_tree'], ['xml_id', 'name', 'context']],                         
        }).then(function (data) { 
            data = data.filter(function(item){
                return item.xml_id == "ims.action_" +  model.substring(4) + "_tree";
            });
            
            if(data.length == 1){                                                                                                                       
                var link = $('<a href="#">' + data[0].name + '</a>');                                                               

                link.on("click", function() {
                    am.doAction({                        
                        action_id: data[0].xml_id,
                        type: "ir.actions.act_window",
                        res_model: model,
                        res_id: false,
                        views: [[false, "list"]],
                        name: data[0].name,
                        context: data[0].context,
                        target: 'main',     //'main' resets the breadcrums
                    });
                });
                
                var li = $('<li class="breadcrumb-item o_back_button" data-hotkey="b" style="position: relative;"></li>');
                li.append(link);
                $(br).prepend(li);

                //TODO: found a bug. Level list --> Level form --> Studies form --> Refresh --> Studies list (from the form) --> Tree does not link anymore even refreshing, using the menu is needed...
            }                                    
        }); 
    }
});