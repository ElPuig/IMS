/** @odoo-module **/

import { registry } from "@web/core/registry";

// Issue #405: a group's classroom changed, but a room collision left TWO teaching blocks
// pending, same teacher/subject, different weekdays (seeded directly via the ORM in
// TestGroupClassroomChangeTour - the write()-time propagation itself is already covered by
// tests/test_group_classroom_change.py). This tour proves the banner + wizard UI actually
// renders and works in a real browser: the banner shows on the group's own form, its button
// opens ems.group_classroom_change_wizard, the reused ems_grouped_conflict_lines widget renders
// both pending blocks as "Room conflict" rows grouped under one sub-group card (same teacher +
// subject), and the sub-group's own BULK classroom picker (developer feedback 2026-09-08, real
// SMX1D/SMX2D usage: picking a room one row at a time for many rows was too slow) resolves both
// rows in a single pick, without touching either row individually.
registry.category("web_tour.tours").add("ems_group_classroom_change_wizard", {
    test: true,
    url: "/odoo/action-ems.action_group_tree",
    steps: () => [
        {
            trigger: ".o_list_view",
            content: "Groups list loaded",
        },
        {
            trigger: ".o_searchview_input",
            content: "Search for the seeded group",
            run: "edit Tour Classroom Change Group",
        },
        {
            trigger: ".o_searchview_input",
            content: "Confirm the search",
            run: "press Enter",
        },
        {
            trigger: ".o_list_view .o_data_row td:contains('Tour Classroom Change Group')",
            content: "Open it",
            run: "click",
        },
        {
            trigger: ".alert-warning:contains('2'):contains('teaching block')",
            content: "The pending-classroom banner shows, naming the two flagged blocks",
        },
        {
            trigger: ".alert-warning button[name='action_open_classroom_change_wizard']",
            content: "Open the resolution wizard",
            run: "click",
        },
        {
            trigger: ".modal .card-header:contains('Room conflict')",
            content: "The reused conflict-lines widget renders both pending blocks as room conflicts",
        },
        {
            trigger: ".modal .ems_conflict_subgroup:has(.ems_conflict_row:eq(1))",
            content: "Both rows landed in the SAME sub-group (same teacher + subject)",
        },
        {
            trigger: ".modal .modal-footer button[name='action_confirm_disabled'][disabled]",
            content: "Confirm shows disabled - both rows still default to the same colliding classroom on both sides",
        },
        {
            trigger: ".modal .ems_conflict_bulk_space_left input",
            content: "Bulk-pick the free third classroom for the whole sub-group's left (pending) side",
            run: "edit Tour Third Space",
        },
        {
            trigger: ".o-autocomplete--dropdown-item:contains('Tour Third Space')",
            content: "Select it",
            run: "click",
        },
        {
            trigger: ".modal .ems_conflict_row:eq(0) .ems_conflict_space_left input",
            content: "The bulk pick applied to the FIRST row without touching it directly",
            run: () => {
                const inputs = [...document.querySelectorAll(".modal .ems_conflict_space_left input")];
                const values = inputs.map((input) => input.value);
                if (!values.every((value) => value.includes("Tour Third Space"))) {
                    throw new Error("Bulk classroom pick did not apply to every row in the sub-group: " + JSON.stringify(values));
                }
            },
        },
        {
            trigger: ".modal .modal-footer button[name='action_confirm']:not([disabled])",
            content: "Confirm is enabled now that both rows resolved in one bulk pick",
            run: "click",
        },
        {
            trigger: ".o_form_view:not(:has(.alert-warning))",
            content: "The pending-classroom banner is gone - nothing left to resolve",
        },
    ],
});
