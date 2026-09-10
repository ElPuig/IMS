/** @odoo-module **/

import { registry } from "@web/core/registry";

// A plain teacher (no hr.group_hr_user) opening the Teachers screen. Its default view is the
// kanban, whose presence icon carries hr_holidays' "hr_presence_status_private" widget - and
// that widget's JS declares current_leave_id (groups="hr.group_hr_user") as a field
// dependency, which goes into the read specification whether or not the reader is allowed the
// field. The backend test (tests/test_employee_presence_widget.py) can only prove the arch is
// right; nothing but a real browser proves what the client actually ends up asking the server
// for, which is where this bug lived: every teacher got "You do not have enough rights to
// access the fields current_leave_id on Employee" instead of the screen.
registry.category("web_tour.tours").add("ems_employee_teacher_kanban", {
    test: true,
    url: "/odoo/action-ems.action_employee_kanban",
    steps: () => [
        {
            // Structural selectors only (see CLAUDE.md's "Tour tests and language"): the
            // fixture's own name is the single piece of text this tour typed itself.
            trigger: ".o_kanban_renderer .o_kanban_record:contains('0000 Teacher Kanban Tour')",
            content: "The Teachers kanban rendered its cards for a plain teacher",
        },
        {
            trigger: ".o_switch_view.o_list",
            content: "Switch to the list view",
            run: "click",
        },
        {
            trigger: ".o_list_view .o_data_row .o_data_cell:contains('0000 Teacher Kanban Tour')",
            content: "The list view opens for a plain teacher too",
        },
        {
            trigger: ".o_list_view .o_data_row .o_data_cell:contains('0000 Teacher Kanban Tour')",
            content: "Open the teacher's form",
            run: "click",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='name']",
            content: "The form opens as well - the presence icon lives there too",
        },
    ],
});
