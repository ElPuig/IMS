/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("ems_teaching_reduction_type_crud", {
    test: true,
    url: "/odoo/action-ems.action_teaching_reduction_type_list",
    steps: () => [
        {
            trigger: ".o_list_view",
            content: "Teaching hour reduction types list view loaded",
        },
        {
            trigger: ".o_list_button_add",
            content: "Click New",
            run: "click",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='code'] input",
            content: "Fill in code",
            run: "edit TOURTRT",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='name'] input",
            content: "Fill in name",
            run: "edit Tour Test Reduction Type",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='reduction_hours'] input",
            content: "Fill in reduction hours",
            run: "edit 2",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save",
            run: "click",
        },
        {
            trigger: ".o_breadcrumb a",
            content: "Navigate back to the list",
            run: "click",
        },
        {
            trigger: ".o_list_view .o_data_row td[name='name']:contains('Tour Test Reduction Type')",
            content: "New record confirmed in list",
        },
        {
            trigger: ".o_list_view .o_data_row td[name='reduction_hours']:contains('2')",
            content: "Reduction hours confirmed in list",
        },
        {
            trigger: ".o_list_view .o_data_row td[name='name']:contains('Tour Test Reduction Type')",
            content: "Open to edit",
            run: "click",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='reduction_hours'] input",
            content: "Change reduction hours",
            run: "edit 4",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save the edit",
            run: "click",
        },
        {
            trigger: ".o_breadcrumb a",
            content: "Navigate back to the list",
            run: "click",
        },
        {
            trigger: ".o_list_view .o_data_row td[name='reduction_hours']:contains('4')",
            content: "Updated reduction hours confirmed in list",
        },
        {
            trigger: ".o_list_view .o_data_row td[name='name']:contains('Tour Test Reduction Type')",
            content: "Open to delete",
            run: "click",
        },
        {
            trigger: ".o_form_view .o_cp_action_menus button",
            content: "Open action menu",
            run: "click",
        },
        {
            trigger: ".o_menu_item:contains('Delete')",
            content: "Click Delete",
            run: "click",
        },
        {
            trigger: ".modal-footer .btn-primary",
            content: "Confirm deletion",
            run: "click",
        },
        // Deleting can land Odoo on an adjacent record's form instead of the list (same
        // observed behaviour as non_teaching_type_tour.js) — force a return to the list either way.
        {
            trigger: ".o_list_view, .o_breadcrumb a",
            content: "Back in list after deletion (navigating there explicitly if needed)",
            run: () => {
                document.querySelector(".o_breadcrumb a")?.click();
            },
        },
        {
            trigger: ".o_list_view",
            content: "Confirmed back in list",
        },
        {
            trigger: ".o_list_view:not(:has(.o_data_row td[name='name']:contains('Tour Test Reduction Type')))",
            content: "Record deleted — no longer in list",
        },
    ],
});
