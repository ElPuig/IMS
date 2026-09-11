# What's new:

## "Schedule" tab on "My Profile":
- Any user's "My Profile" screen now has a "Schedule" tab, showing exactly the same weekly schedule (same `schedule_grid` widget) as their linked teacher/employee record's own "Schedule" tab, with the same edit permission (Department Chiefs only). It's the first tab, shown by default when opening "My Profile".
- Bridged via two new related fields on `res.users` (`can_edit_schedule`, `schedule_attendance_ids`) — no override of `res.users`' own native `resource_calendar_id` (from the `resource` module) was needed, since it already resolves to the same calendar as the linked employee's.

## Tab order on "My Profile":
- All tabs reordered to: Schedule, Work Information, HR Settings, Private Information, Account Security, Devices, Resume, Preferences.

# Changes:

## "My Profile" trimmed down, while keeping full admin access:
- The main form, "Location" (Department, Address) and the "HR Settings" tab keep their existing behaviour: read-only/hidden for an ordinary self-viewing user, still fully editable/visible for an administrator (including anyone with the EMS "Administrator (académico)" role, which already grants this transitively) — unchanged from before, just confirmed and documented (an earlier draft of this work briefly forced these read-only/hidden for everyone, including administrators, before being corrected).
- "Manager" and "Coach" in the main form are now unconditionally read-only, even for an administrator — both are set from the department screens, never hand-edited from "My Profile".
- The "Preferences" tab now only shows "Disable profile picture" and "Language" for an ordinary self-viewing user — Email, Timezone, Signature and `calendar`'s own "Calendar Default Privacy" are hidden, but (like the rest of this list) stay fully visible for an administrator.
- The Approvers section (who approves an absence/attendance correction) is now unconditionally read-only, even for an administrator — it's derived from the department hierarchy, never something to hand-edit from here. Both approver fields now show an avatar (previously only the attendance one did).
- "Private Information" (address, citizenship, marital status, education, dependants, emergency contact, work permit) is now always editable for everyone, including an ordinary self-viewing user — it's the user's own personal, not professional, data, and they're always free to modify it.

## Attendance approver now always matches the absence approver:
- `hr.employee.attendance_manager_id` (native `hr_attendance` field, previously always empty since nothing in EMS ever set it) is now a stored compute that mirrors `leave_manager_id` (the Area Manager of the employee's top-level department) — the same person is meant to approve both, so there is no reason for the two to diverge. No migration needed: Odoo's own module-upgrade machinery recomputed it for every existing employee automatically.

# Internal changes:

## Shared schedule widget generalized to work outside the teacher's own form:
- The `schedule_grid` widget (reused by the teacher form, groups, and now "My Profile") previously assumed its host record always *was* an `hr.employee` for its employee-specific RPCs (derived breaks, PDF export, "copy from another teacher"), which crashed with a "Missing Record" error when reused on `res.users`. Generalized to resolve the real employee id from either the host record itself or a bridged `employee_id` field, whichever is present.

## Merge conflicts (this branch vs. an already-integrated one touching the same shared file):
- `tests/__init__.py`: purely additive, kept both branches' new imports.
- `i18n/ca_ES.po` / `i18n/es_ES.po`: both branches added a `#:` reference to the same existing "Schedule" msgid block (one for `res.partner.schedule_attendance_ids`, already there from #408; one for `res.users.schedule_attendance_ids`, new here) - per CLAUDE.md's "a msgid diff alone is not enough" rule, merged both reference lists into the one block rather than picking a side, so both fields stay translated.

## Role-based smoke tours (#434/#437): reviewed, no change needed:
- The screen this branch adds ("My Profile", reached via `hr.res_users_action_my`/the user-menu, not any `ir.ui.menu` entry) is structurally unreachable by the per-role crawler, which only iterates `menuService.getAll()`. The one file genuinely shared with a crawler-reachable screen (`schedule_grid_field.js`, also touched by #439 via the "Teachers" blank-create form) only gained a backward-compatible `_employeeIdFor()` fallback - re-ran the 5 role-smoke tours after the merge, all green.

## Flaky failure found and fixed in this branch's own dedicated tour (not a production bug):
- `TestUserProfileTour.test_user_profile_tabs_tour_ordinary_user` failed deterministically post-merge: Odoo's own tour harness (`odoo/tests/common.py`'s post-tour `.o_form_dirty` DOM check) flagged the "My Profile" form as left with unsaved changes right after a real, successful save. Root-caused with a throwaway diagnostic step logging every `.o_form_dirty` node: by the very next tour step, there were zero - proving the record's own "isDirty" recompute (which drives that CSS class) lands one render tick after the saved field value is already visible in the DOM, and the tour was ending exactly in that one-tick window. Not a real leftover-dirty-state bug in the save path (confirmed empirically, not just by reasoning about it) - fixed by adding a final step that explicitly waits for `.o_form_view:not(.o_form_dirty)` before letting the tour end. Verified 3/3 clean re-runs after the fix.

# Related with:
- Closes #440
