# Internal changes:

## Role-based tour coverage: per-role smoke tours (issue #434 follow-up):
- `78` of the `89` existing browser tours logged in as `admin` (or a role implying
  `hr.group_hr_user`/`group_system`), which is why issue #434 (a widget field dependency
  bypassing the view arch's group-based stripping) reached production unnoticed - every
  existing Teachers/ASP tour happened to run as a role the bug couldn't affect.
- `tests/common.py`: `ROLE_GROUP_XMLIDS`, `create_role_user()`, `create_role_employee()` -
  shared factory replacing the same ~15-20 line `res.users.create()` block hand-written
  independently across 9 existing tour test files (`test_student_data_reader_tour.py`,
  `test_employee_teacher_kanban_tour.py`, `test_attendance_session_tour.py`,
  `test_attendance_passlist_tour.py`, `test_attendance_correction_tour.py`,
  `test_contact_group_change_tour.py`, `test_employee_staff_permissions_tour.py`,
  `test_grade_tutor_matrix_tour.py`, `test_student_my_groups_tour.py`), all retrofitted onto it.
- `static/tests/tours/role_smoke_common.js`: a generic crawler (`crawlAccessibleScreens`) that
  fetches the exact menu tree the real webclient uses for the logged-in session (already
  filtered server-side by that session's own groups) and opens every reachable window
  action/view_mode, asserting nothing about the data - only that nothing crashes. Uses
  `actionService.loadAction()` rather than reading `ir.actions.act_window` directly (that model
  is only ACL-readable by Administration/Settings). Forces `action.limit = 1` and preloads
  `web.assets_backend_lazy` up front so real dev-DB data volume and lazy-widget loading can't
  slow down or destabilize a check that never needed either.
- 5 new tours (`tests/test_role_smoke_<role>_tour.py` + matching
  `static/tests/tours/role_smoke_<role>_tour.js`) for `teacher` (the actual #434 role),
  `orientation` (zero direct ACL rows of its own), `coexistence` (same implied-group shape,
  with write access), `secretary` (heaviest ACL footprint of any EMS role, 70 rows), and `tac`
  as a deliberate negative control (it DOES imply `hr.group_hr_user`, and correctly surfaces no
  findings).
- Validated end-to-end against the real #434 regression: temporarily reverted the
  `views/community/employee/kanban.xml` fix, confirmed the new `teacher` tour fails exactly on
  the Teachers/ASP kanban actions with a clear diagnostic message, then restored the fix and
  confirmed green again.
- `CLAUDE.md`: Development-workflow rule change - a new/changed tour must log in as the
  least-privileged role from the Spec step's access-control table (not `admin` by default), and
  must visit every `view_mode` of the action under test. New "Per-role smoke tours" entry under
  Testing conventions documents the mechanism, its 5-role roster, and skip-list maintenance.
- `plans/role_tour_coverage_retrofit.md`: bounded, ongoing backlog for retrofitting existing
  admin-only tours whose real least-privileged role doesn't imply `hr.group_hr_user` - not done
  as part of this branch.
- Two secretary-specific findings are real but not yet root-caused, temporarily skip-listed with
  their own tracking plans: `plans/role_smoke_student_kanban_secretary_hang.md` (opening the
  Students kanban as secretary hangs indefinitely client-side - no server error, just never
  resolves) and `plans/role_smoke_secretary_unexplained_findings.md` (4 unrelated actions -
  `ems.attendance_template`, `ems.attendance_session`, `ems.strike`, native `calendar.event` -
  fail with a generic client-side error with zero server-side trace, reproducing only through
  this crawler's rapid pace; existing dedicated tours already open the same screens successfully
  for other logins).

# Changes:

## Secretary staff now land on Educational Community, teachers on the attendance roll-call screen (issue #440):
- Found while live-testing a real secretary account: opening the app used to send every internal
  user, regardless of role, straight into the daily attendance roll-call screen. A plain
  secretary account browsing it saw every teacher's ongoing session for the day dumped into a
  "take attendance" UI, because the screen's own data query only ever narrowed results down to
  "my own sessions" for an academic admin - any other non-teaching role fell through that check
  and saw everything, unfiltered, instead of the intended empty state.
- The roll-call screen's own default view now correctly shows nothing for anyone without a real
  teaching assignment, while a genuine admin without one still sees everything (so admin still
  has full oversight/override ability, unchanged).
- Non-teaching staff (secretary) no longer see the "Current"/roll-call menu entry at all, and now
  land on "Educational Community" by default when logging in instead of the attendance app -
  both the app's own default and every existing account were updated, plus the template used to
  onboard new non-teaching accounts, so this applies going forward automatically.
- Separately, every real teacher account (and the template used to onboard new ones) now
  consistently lands on the roll-call screen by default too, instead of the read-only history
  list some of them had been defaulting to.

# Fixes:

## Secretary missing read access to strike/attendance-status data needed to browse student history:
- `ems.strike.reason` and `ems.attendance_status` had no read access for the secretary role at
  all (only teacher/admin and, for the strike reason catalog, the shared orientation/coexistence
  reader group) - browsing a student's attendance/discipline history as secretary hit an access
  error the moment either was needed to render a label.
- `ems.strike` itself had no visibility rule for secretary either - even after granting the ACL
  read right above, secretary would have seen zero strike records at the database level. Added a
  read-only "all data" rule matching the existing coexistence one, since secretary needs the same
  centre-wide history access.

## Two non-existent widget references, found via the new role-smoke crawler:
- `views/attendance/attendance_template/form.xml`: `widget="timepicker"` on `start_date`/
  `end_date` (plain `Date` fields, `column_invisible`) - the widget name doesn't exist anywhere
  in this Odoo version, confirmed via grep across every installed addon. Removed; the fields
  were never actually visible anyway (kept only for internal compute).
- `views/attendance/attendance_session/form.xml`: `widget="one2many_list"` on
  `attendance_session_line_ids` - also not a registered widget name. Removed, letting the field
  fall back to its default one2many rendering (already fully specified by its nested list
  sub-view). Both silently fell back with a console warning rather than a visible failure,
  which is why neither had ever been noticed before. Existing
  `TestAttendanceTemplateTour`/`TestAttendanceTemplateColorTour`/`TestAttendanceSessionTour`
  tours confirmed unaffected.
