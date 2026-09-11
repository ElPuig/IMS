# What's new:

## Student form: new "Schedule" tab (issue #408):
- Adds a read-only "Schedule" tab to the student form (`views/community/contact/form.xml`), showing the student's own weekly timetable — subjects, teachers, classrooms, breaks — plus a "Subject → Teacher(s)" summary and a PDF export, exactly matching the existing group form's own Schedule tab.
- Unlike a group's schedule (which shows one group's *whole* week), a student's is scoped to the subjects they're actually enrolled in — matched per `(subject_id, group_id)` enrollment pair, not by their main group alone — so a subject taught to their main group that they were never enrolled in never leaks into their own view.
- A student can be enrolled through more than one group at once (electives, reinforcement), so unlike a group's or a teacher's own schedule, a student's can show genuinely overlapping classes. The read-only schedule widget now lays out any two overlapping blocks side by side instead of silently stacking one on top of the other — this also fixes the same latent (rare) overlap-rendering gap on the group's own Schedule tab, which never had this handling before.

# Fixes:

## Group and student schedule tabs no longer show duplicated, out-of-date classes (issue #408):
- Both the group's and the (new) student's Schedule tab could silently show a stale, archived copy of a subject alongside the real, current one — often at genuinely overlapping times, since the two versions' hours rarely matched. Root cause: neither tab's aggregation forced `active_test=True` on its own search, so opening either from a context that had already disabled active-record filtering for an unrelated reason (the Students list itself does this, so withdrawn/graduated students still show up there) let a past course transition's archived calendar entries leak back in as if they were still current. Found live on real data while testing the new student tab (two real students each showed a full duplicate set of their subjects).
- Both computes now force `active_test=True` on every `resource.calendar`/`resource.calendar.attendance` search, regardless of the surrounding request's own context.

# Internal changes:

## Group/student schedule code sharing (issue #408):
- The group form's Schedule tab and the new student one now share the exact same OWL widget (renamed `group_schedule_grid` → `readonly_schedule_grid`, `GroupScheduleGridField` → `ReadonlyScheduleGridField`) and the exact same server-side report-building pipeline (moved from `ems.group`'s own file into the shared `ems.schedule_report_mixin`, now also used by `res.partner`) — reusing the group's tab for the student's was implemented as "change the search, not the widget", per the explicit ask.
- Added a generic interval-overlap-clustering + column-assignment helper (`layoutOverlappingBlocks`, `schedule_grid_geometry.js`) — the same shape of algorithm calendar-app day views commonly use — shared by both schedule widgets.

## Student schedule tab's own tour now logs in as a teacher, not admin (issue #408 follow-up):
- Reviewed whether this feature's merge needed any change to the per-role smoke tours (issue #434/#437): it doesn't — the only menu entry point that would reach an existing student's form in the crawler (`ems.action_student_kanban`) is already skip-listed there for an unrelated, pre-existing hang, so the new tab is never reached by that crawler for any role either way.
- A real, adjacent gap was found instead: the tab's own dedicated tour only ever verified via `login="admin"`, which the project's own post-#434 convention calls out as exactly the pattern that can hide an `AccessError` a less-privileged role would actually hit. Verified empirically (not just by reading the access table) that the tab renders cleanly for a plain teacher login, then switched the test to that login permanently.
