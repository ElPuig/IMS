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
            //TODO: the "Subject" breadcrum dissapears when jumping to another models, so its needed to 
            //know why it's not appearing. Maybe is because there's no native subject list? It's because the redirection from "subject_view" list to "subject" form?
            if (this.env.config.viewType == "form" && this.env.searchModel.resModel == "ims.subject") {
                if(this.breadcrumbs.length == 1){
                    if(this.env.searchModel.context["subject_view_controller"] != null && this.breadcrumbs[0].jsId != this.env.searchModel.context["subject_view_controller"].jsId){
                        // This is the clean way and should be used always (the context value is setup on "list_renderer_customs.js").
                        this.breadcrumbs.unshift(this.env.searchModel.context["subject_view_controller"]);
                    }
                    else{
                        // TODO: this is a workaround, should be fixed properly!
                        // Details of the workaround (please, fix!): The first time, the controller_id is the same for the current form than for the list view...
                        // Entering again changhes the list's controller_id... WHY?
                        var self = this;
                        var br = $(this.root.el).find("ol.breadcrumb");
                        if($(br).children("li").length == 1){                                                        
                            rpc.query({
                                model: 'ir.actions.act_window',
                                method: 'search_read',
                                //TODO: domain not working, try to get the main model in order to avoid looping in the result!
                                //args: [['xml_id', '=', 'ims.action_subject_tree'], ['xml_id', 'name', 'context']],
                                args: [[], ['xml_id', 'name', 'context']],
                            }).then(function (data) {  
                                data = data.filter(function(item){
                                    return item.xml_id == 'ims.action_subject_tree';
                                });
                                
                                if(data.length == 1){                                                                                          
                                    var link = $('<a href="#">' + data[0].name + '</a>');                                                               
                                    link.on("click", function() {
                                        self.gotoSubject(data[0].name, data[0].context);
                                    });
                                    
                                    var li = $('<li class="breadcrumb-item o_back_button" data-hotkey="b" style="position: relative;"></li>');
                                    li.append(link);
                                    $(br).prepend(li);
                                }                                    
                            });                           
                        } 
                    }
                }
            }
        });
    },
    
    gotoSubject(){
        var am = ActionService.start(this.env); 
        rpc.query({
            model: 'ir.actions.act_window',
            method: 'search_read',
            //TODO: domain not working, try to get the main model in order to avoid looping in the result!
            //args: [['xml_id', '=', 'ims.action_subject_tree'], ['xml_id', 'name', 'context']],
            args: [[], ['xml_id', 'name', 'context']],
        }).then(function (data) {            
            data.forEach(function(item){
                if(item.xml_id == 'ims.action_subject_tree'){                                                            
                    am.doAction({                        
                        action_id: 'action_subject_tree',
                        type: 'ir.actions.act_window',
                        res_model: 'ims.subject_view',                
                        res_id: false,
                        views: [[false, "list"]],
                        name: item.name,
                        context: item.context
                    });
                }
            });
        });
    },
});