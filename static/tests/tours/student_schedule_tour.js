/** @odoo-module **/

import { registry } from "@web/core/registry";

// Covers the student form's own "Schedule" tab (views/community/contact/form.xml) - the
// read-only aggregation widget (schedule_grid_readonly_field.js, widget="readonly_schedule_grid")
// reused as-is from the group's own Schedule tab (see group_tour.js's own equivalent steps),
// this time backed by res.partner.schedule_attendance_ids instead of ems.group's. A clean
// TransactionCase/PDF-render test only proves the Python side works - this is what actually
// catches a client-side (OWL template/widget) crash, per CLAUDE.md's DTON "T" step.
registry.category("web_tour.tours").add("ems_student_schedule_tab", {
    test: true,
    url: "/odoo/action-ems.action_student_kanban",
    steps: () => [
        {
            trigger: ".o_kanban_view, .o_list_view",
            content: "Students view loaded",
        },
        {
            trigger: ".o_searchview_input",
            content: "Search for the test student",
            run: "edit Tour Schedule Student",
        },
        {
            trigger: ".o_searchview_input",
            content: "Confirm the search",
            run: "press Enter",
        },
        {
            trigger: ".o_kanban_record:contains('Tour Schedule Student'), .o_data_row td:contains('Tour Schedule Student')",
            content: "Open the test student",
            run: "click",
        },
        {
            trigger: ".o_form_view .o_notebook .nav-link:contains('Schedule')",
            content: "Open the Schedule tab",
            run: "click",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='schedule_attendance_ids']",
            content: "Schedule tab rendered without crashing",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='schedule_attendance_ids'] .o_schedule_grid_entry",
            content: "The student's own teaching entry renders as a real block in the grid",
        },
        {
            trigger: ".o_form_view .o_field_widget[name='schedule_attendance_ids'] .o_schedule_grid_toolbar button:contains('PDF')",
            content: "The PDF export button is available",
        },
    ],
});
