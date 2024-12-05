/** @odoo-module **/
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { patch } from "@web/core/utils/patch";
import { useRef, onPatched, onMounted, useState } from "@odoo/owl";

patch(ControlPanel.prototype, "control_panel_customs", {
    setup() {        
        this._super.apply(this, arguments);    
               
        owl.onMounted(() => {
            if (this.env.config.viewType == "form" && this.env.searchModel.resModel == "ims.subject") {                
                var br = $(this.root.el).find("ol.breadcrumb");
                // TODO: maybe history.back() can be changed to the correct URL (check this.env or whatever).
                // TODO: this is missing when entering another form, maybe can be added to the this.breadcrumb object?
                $(br).prepend('<li class="breadcrumb-item o_back_button" data-hotkey="b" style="position: relative;"><a href="javascript:history.back();">Subjects</a></li>')
            }
        });
    },    
});