# Fixes:

## Schedule tab: editing a period lost every group but the first:
The "Schedule" tab's edit widget (`schedule_grid_field.js`) only ever kept a single group per
card, even though `resource.calendar.attendance.group_ids` is a real Many2many and the server
side (`ems.attendance_template`, `ems.teaching`, `apply_schedule_changes`) already treats it as
a genuine set. A period where one teacher runs an identical session for two groups at once in
the same room (e.g. an optional subject combining two official groups) showed only its first
group when re-opened for editing, and saving it silently dropped every other group the period
actually had. The group picker now carries every selected group through load, edit and save,
shown as removable tags with a search-as-you-type field to add more (a first attempt used a
native multi-select, but the developer found it impractical — no visible selected state, and
picking several required a hidden Ctrl/Shift-click). Reported as issue #439 (Cristian Escobar's
Monday 17-18 subject 1709 session, taught to GA1C and GA1D at once in room 2.17).

# Internal changes:

## Role-based smoke tours (#434/#437): reviewed, actually re-run, no regression:
Unlike the other 439-era branches, this one genuinely touches a screen the per-role crawler
tours reach today: `action_employee_kanban` ("Teachers" menu) has no `res_id`, so the crawler's
generic `doAction(..., {viewType: 'form'})` opens a blank employee in create mode with
`default_employee_type: 'teacher'` - which renders this exact Schedule tab/widget (empty grid,
but the same component, now using `groupIds` arrays instead of a scalar `groupId` throughout).
Checked which of the 5 roster roles actually reach that menu at all: Odoo's own menu-visibility
filter (`ir.ui.menu._visible_menu_ids`) hides any act_window menu whose model the user can't
read, and `hr.employee` has no ACL row for `ems.group_secretary` - only `ems.group_teacher`
(read) and `ems.group_academic_admin` (full) - so `teacher`, `tac`, `orientation` and
`coexistence` (all imply `group_teacher`) see it, `secretary` does not. Re-ran the 4 affected
role-smoke tours after the merge (`./test.sh
'/ems:TestRoleSmokeTeacherTour,/ems:TestRoleSmokeTacTour,/ems:TestRoleSmokeOrientationTour,/ems:TestRoleSmokeCoexistenceTour'`):
0 failed, 0 errors - the new `AutoComplete`-based group picker initializes cleanly on a blank,
unsaved record, so no change was needed to the crawler or its skip list.

# Related with:
- Closes #439
