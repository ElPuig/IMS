/** @odoo-module **/

import { Component } from "@odoo/owl";

// Shared crawler for the per-role smoke tours - see CLAUDE.md's "Per-role smoke tours" (issue
// #434 follow-up). Each role's own tour file (role_smoke_<role>_tour.js) is a thin wrapper
// around crawlAccessibleScreens() below, registered under its own role-specific tour name so
// each lands as its own test class/shard.
//
// Instead of a hand-authored step list, this fetches the exact menu tree the real webclient
// would (already filtered server-side by the logged-in session's own groups, via the "menu"
// service) and opens every reachable window action in every view_mode it declares. It asserts
// nothing about the data shown - only that nothing crashes. Detection needs no bespoke
// error-dialog checking: Odoo's own tour/HttpCase harness already fails the test on any
// console.error, and the webclient's error service logs every uncaught client error that way
// (including an AccessError surfaced while a view fetches its data - exactly how #434 itself
// would have been caught here). `Component.env` (set by web/static/src/start.js on every
// webclient boot) is used instead of a step's own `this` context, which the tour engine binds
// to `{anchor}` only.
//
// Maintaining this list: add an action's xml_id here only for a CONFIRMED false positive - a
// deliberate business-rule guard (typically a UserError raised from default_get()/create() for
// a role that legitimately cannot use that screen), not to silence a genuine finding. xml_id
// (not the numeric action id, which varies per database) is what keeps this list portable
// across environments - see CLAUDE.md's "Per-role smoke tours".
const SKIP_ACTION_XMLIDS = new Set([
    // ems.enrollment's default_get() deliberately raises UserError("Only admins and secretary
    // staff can create manual enrollments.") for anyone else - a pre-existing, documented
    // limitation (models/contacts/enrollment.py's own "TODO: unable to hide the NEW button
    // based for only tutors..."), not an unintended crash. Found 2026-09-11 via the `teacher`
    // spike run.
    "ems.action_enrollment_tree",
    // ems.attendance_justification's default_get() deliberately raises UserError("Only tutors
    // can justify student's attendances.") for a non-tutor teacher - same shape, same
    // pre-existing TODO (models/attendance/attendance_justification.py). Found 2026-09-11.
    "ems.action_attendance_justification_tree",
]);

export async function crawlAccessibleScreens() {
    const { action: actionService, menu: menuService } = Component.env.services;

    const actionIds = [...new Set(
        menuService.getAll()
            .filter((item) => item.actionModel === "ir.actions.act_window" && item.actionID)
            .map((item) => item.actionID)
    )];
    if (!actionIds.length) {
        throw new Error("Role smoke tour found no reachable window actions for this role's menu - " +
            "check the role's group/menu access before trusting a green run.");
    }

    const failures = [];
    for (const actionId of actionIds) {
        let action;
        try {
            // loadAction() (not orm.read on ir.actions.act_window directly) - the model itself
            // is only readable by Administration/Settings; loadAction's own server route
            // (/web/action/load) reads it with sudo() deliberately, since resolving the action
            // behind a menu click must work for every internal user regardless of that ACL.
            action = await actionService.loadAction(actionId);
        } catch (error) {
            failures.push(`Action ${actionId}: failed to load - ${error.message || error}`);
            continue;
        }
        if (!action || action.target === "new" || SKIP_ACTION_XMLIDS.has(action.xml_id)) {
            continue; // Wizards/dialogs, or a confirmed false positive - see SKIP_ACTION_XMLIDS.
        }
        for (const viewType of (action.view_mode || "").split(",").map((type) => type.trim()).filter(Boolean)) {
            try {
                await actionService.doAction(action, { viewType, clearBreadcrumbs: true });
            } catch (error) {
                failures.push(`Action ${actionId} (${action.name}), view=${viewType}: ${error.message || error}`);
            }
        }
    }
    if (failures.length) {
        throw new Error(`${failures.length} screen(s) failed for this role:\n${failures.join("\n")}`);
    }
}
