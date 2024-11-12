/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { actionService } from "@web/webclient/actions/action_service";

var BasicRenderer = require('web.BasicRenderer');
var FormRenderer = BasicRenderer.extend({
    className: "transient_enrollment",
    events: _.extend({}, BasicRenderer.prototype.events, {
        'click .o_list_many2one': '_onTransientClick',        
    }),
    _onTransientClick(record){
        console.log("HOLA");
    }
})

patch(ListRenderer.prototype, "transient_enrollment_click", {
    setup() {
        this._super.apply(this, arguments);
    },

    onClickCapture(record, ev){
        if(record.resModel == "ims.transient_enrollment"){
            ev.preventDefault();
            ev.stopPropagation();
            
            var rpc = require('web.rpc');
            // TODO: "this" is not ok, which object should be used?
            // Maybe call the python method to open the form through RCP? https://www.odoo.com/pl_PL/forum/pomoc-1/hi-how-call-a-function-python-in-file-javascript-in-odoo-15-please-help-216189

            rpc.query({
                model: 'res.partner',
                method: 'open_form_view_contact_by_id',
                args: [[], record.fields.student_id],
            }).then(function (result) {
                console.log(result);
            });          
        }        
    },
       
    _renderRow: function (record) {
        console.log("_renderRow");
        
        let row = this._super(record);
        var self = this;
        if (record.model == "ims.transient_enrollment") {
            row.addClass('o_list_no_open');
            // add click event
            row.bind({
                click: function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    self.do_action({
                        type: "ir.actions.act_window",
                        res_model: "res.partner",
                        res_id: record.student_id,
                        views: [[false, "form"]],
                        target: "target",
                        context: record.context || {},
                    });
                }
            });
        }
        return row;
    },
});

/*
var ListRenderer = require("web.ListRenderer");
var CustomListRenderer = ListRenderer.include({

    // events: _.extend({}, ListRenderer.prototype.events, {
    //     'click thead th.o_column_sortable': '_onSortColumn',
    // }),

    // _onSortColumn: function (ev) {
    //     if (this.$el.hasClass('disable_sort')) {
    //         ev.preventDefault();
    //         return false;
    //     }
    //     return this._super.apply(this, arguments);
    // },
    _renderRow: function (record) {
        console.log("_renderRow");
        
        let row = this._super(record);
        var self = this;
        if (record.model == "ims.transient_enrollment") {
            row.addClass('o_list_no_open');
            // add click event
            row.bind({
                click: function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    self.do_action({
                        type: "ir.actions.act_window",
                        res_model: "res.partner",
                        res_id: record.student_id,
                        views: [[false, "form"]],
                        target: "target",
                        context: record.context || {},
                    });
                }
            });
        }
        return row;
    },
});

return CustomListRenderer;

ListRenderer.include({
    _renderRow: function (record) {
        console.log("_renderRow");
        
        let row = this._super(record);
        var self = this;
        if (record.model == "ims.transient_enrollment") {
            row.addClass('o_list_no_open');
            // add click event
            row.bind({
                click: function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    self.do_action({
                        type: "ir.actions.act_window",
                        res_model: "res.partner",
                        res_id: record.student_id,
                        views: [[false, "form"]],
                        target: "target",
                        context: record.context || {},
                    });
                }
            });
        }
        return row;
    },
});

*/