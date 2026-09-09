/** @odoo-module **/

import { registry } from "@web/core/registry";

// Last deferred follow-up of issue #405: a group's classroom (space_id) can drift from where it
// actually meets - resolved here by suggesting the room the group really spends its hours in
// (suggested_space_id) whenever the group's OWN room has zero real teaching hours. Two groups are
// seeded (TestGroupClassroomSuggestionTour), both genuinely drifted at first; this tour applies
// the suggestion for one of them (banner + button on the form) and confirms the "Classroom drift"
// list filter correctly drops it while still showing the other, untouched one, then confirms the
// list's own space_id column reflects the applied change (not just the form).
registry.category("web_tour.tours").add("ems_group_classroom_suggestion", {
    test: true,
    url: "/odoo/action-ems.action_group_tree",
    steps: () => [
        {
            trigger: ".o_list_view",
            content: "Groups list loaded",
        },
        {
            trigger: ".o_searchview_dropdown_toggler",
            content: "Open the search dropdown",
            run: "click",
        },
        {
            trigger: ".o_filter_menu .o_menu_item:contains('Classroom drift')",
            content: "Enable the 'Classroom drift' filter",
            run: "click",
        },
        {
            trigger: ".o_list_view .o_data_row td:contains('Tour Classroom Suggestion Group')",
            content: "The seeded, still-drifted group shows up filtered - open it",
            run: "click",
        },
        {
            trigger: ".alert-info:contains('Tour Suggested Space')",
            content: "The suggestion banner names the room the group actually meets in",
        },
        {
            trigger: ".alert-info button[name='action_apply_suggested_space']",
            content: "Apply the suggested classroom",
            run: "click",
        },
        {
            trigger: ".o_form_view:not(:has(.alert-info))",
            content: "The suggestion banner is gone - nothing left to apply",
        },
        {
            trigger: ".o_breadcrumb a",
            content: "Back to the list - the 'Classroom drift' filter is still active",
            run: "click",
        },
        {
            trigger: ".o_list_view .o_data_row td:contains('Tour Classroom Suggestion Control Group')",
            content: "The untouched control group is still filtered in",
        },
        {
            trigger: ".o_list_view .o_data_row td:contains('Tour Classroom Suggestion Control Group')",
            content: "The just-fixed group no longer matches the drift filter - only the control group remains",
            run: () => {
                const rows = [...document.querySelectorAll(".o_list_view .o_data_row")];
                if (rows.length !== 1) {
                    throw new Error("Expected exactly one row left under the 'Classroom drift' filter, found " + rows.length);
                }
            },
        },
        {
            trigger: ".o_searchview_dropdown_toggler",
            content: "Open the search dropdown again",
            run: "click",
        },
        {
            trigger: ".o_filter_menu .o_menu_item:contains('Classroom drift')",
            content: "Turn the filter back off to find the fixed group again",
            run: "click",
        },
        {
            trigger: ".o_searchview_input",
            content: "Search for the fixed group by name",
            run: "edit Tour Classroom Suggestion Group",
        },
        {
            trigger: ".o_searchview_input",
            content: "Confirm the search",
            run: "press Enter",
        },
        {
            trigger: ".o_list_view .o_data_row td:contains('Tour Suggested Space')",
            content: "The list's own space_id column reflects the applied classroom, not just the form",
        },
    ],
});
