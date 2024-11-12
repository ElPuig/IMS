/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, "transient_enrollment_click", {
    setup() {
        this._super.apply(this, arguments);
    },

    onClickCapture(record, ev){
        console.log("onClickCapture");
        debugger;
        if(record.resModel == "ims.transient_enrollment"){
            ev.preventDefault();
            ev.stopPropagation();

            // TODO: "this" is not ok, which object should be used?
            this.do_action({
                type: "ir.actions.act_window",
                res_model: "res.partner",
                res_id: record.student_id,
                views: [[false, "form"]],
                target: "target",
                context: record.context || {},
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