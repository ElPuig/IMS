/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class SubjectViewListController extends ListController {
   setup() {
       super.setup();
   }
   onClick() {
        this.actionService.doAction({
            //name: 'Open: Students', //to fit with the other regular student's tab
            type: 'ir.actions.act_window',
            res_model: 'ims.subject',                
            res_id: false,
            views: [[false, "form"]],                               
            target: 'current', //with 'new' the form opens as a modal window.
            context: {},
      });
   }
}
registry.category("views").add("subjectview_create_button", {
   ...listView,
   Controller: SubjectViewListController,
   buttonTemplate: "subjectview_create_button.ListView.Buttons",
});