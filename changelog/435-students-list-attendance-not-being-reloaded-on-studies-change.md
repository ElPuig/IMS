# Fixes

## Attendance rosters (and open grade sessions) not updated when a non-admin enrolls a student:

- `ems.enrollment.create()`/`unlink()` cascade the change into every matching
  `ems.attendance_schedule.student_ids` roster and into every open `ems.grade_session`. Both
  cascades used to run with the acting user's own rights, and both target models are
  access-restricted in ways `ems.enrollment` is not, so the acting user silently decided how much
  of the cascade actually happened: an academic admin synced everything (which is why this went
  unnoticed), a teacher - including a secretary who also teaches - only ever saw the templates and
  grade sessions they teach themselves (`rule_attendance_template_teacher_own`,
  `rule_attendance_schedule_teacher_own`, `rule_grade_session_teacher_own`), so the search returned
  nothing and the whole cascade was a silent no-op, and a secretary with no teaching hit an
  `AccessError` instead (read-only ACL on both attendance models).
- Found in production: a secretary who also teaches moved seven ex-ESO students into SA1A from the
  student form's *Enrollment Data* list. All seven `ems.enrollment` rows were created correctly and
  none of them reached a single one of that group's 25 attendance schedule lines, so the teachers'
  roll-call lists never showed them. Measured over the whole production database: 189 (line,
  student) pairs missing across 51 active schedule lines, every single one of them traceable to
  enrollments created by that same non-admin user.
- Fixed by running the cascade helpers under `sudo()` (`_ems_matching_attendance_schedules`,
  `_ems_still_enrolled`, both `_ems_sync_grade_session_*` searches): they are a system-level
  consequence of an enrollment change that was already authorized when the row was created or
  deleted, not a separate action the user has to be independently entitled to perform - the same
  reasoning `_ems_move_group()` already documented for its own `sudo()`. The Python-level guards
  (`default_get()`'s admin/secretary check, `unlink()`'s scored-grades check) are unaffected and
  still run.

## Scored-grades delete guard could not see other teachers' grades:

- `ems.grade_session._ems_has_scored_grades()` - the guard that blocks deleting an
  `ems.enrollment` once evaluation has started - searched the grade lines with the acting user's
  own rights too. A teacher only sees their own sessions, so the guard answered "no grades" for
  another teacher's session and let the enrollment (and its grade lines) be deleted. A guard that
  sees less than everything is weaker, not safer, so its searches now run under `sudo()`.

# Internal changes

## Regression coverage for the enrollment cascades under real, restricted users:

- `tests/test_enrollment.py::TestEnrollmentSyncAsRestrictedUser` drives the create/unlink cascades
  as a secretary-who-also-teaches and as a plain secretary against a template owned by a different
  teacher, asserting the roster is filled and cleared on *every* schedule line of the template and
  that an open grade session gets the new student's lines. Every pre-existing test for these hooks
  ran as superuser, which is exactly why the gap survived.

## Design plan for publishing documents to the centre's Plone website:

Added `plans/web_publications.md`, a design-only note (no code) for automating the publication of
EMS-generated PDFs — group timetables first — to the centre's public website. Recorded here
because the file rides along in this branch, unrelated to the attendance/enrollment fixes above.
Verified live that `https://elpuig.xeill.net/` runs Plone 5.2 with `plone.restapi` already
installed and answering, so no server-side add-on work is needed. Proposes a generic
`ems.web_publication` model plus a `plone_mixin` transport, surfaced as a "Website" entry under
Communications, with a mandatory dry-run flag so development databases can never write to the
public site.

## Existing attendance rosters healed on upgrade:

`migrations/18.0.0.24.2/post-migrate.py` restores the students the broken cascade never wrote:
for every active schedule line it adds whoever is enrolled in its template's subject and groups
but is missing from its roster. Add-only and idempotent - it never removes anybody, so a roster
deliberately customised for one weekly slot survives untouched, unlike the "Reload students"
button which wipes first. No `post_init_hook` counterpart: a fresh installation has no enrollments
to heal. Rehearsed against a restored copy of production: 189 entries across 51 lines restored,
zero missing afterwards, and a second run adds nothing.

## Migration merge conflict (two branches both added `migrations/18.0.0.24.2/post-migrate.py`):

Integrating this branch conflicted with an already-merged, unrelated fix (issue #440 - teacher/
secretary home-action defaults) that had claimed the same still-unreleased version folder.
Resolved per CLAUDE.md's "Merging/rebasing across branches that each add migration scripts":
kept both sides' helper functions in the one file and call all three
(`_default_teachers_to_passlist`, `_default_secretary_to_community`, `_heal_attendance_rosters`)
from a single `migrate()`, rather than keeping duplicate files or dropping either side. Verified
`git tag` still shows `v18.0.0.24.1` as the latest release, confirming `18.0.0.24.2` is the correct,
unreleased folder for both. Re-ran `./upgrade.sh` clean and the new backend test class
(`TestEnrollmentSyncAsRestrictedUser`, 4/4) after resolving.

## Role-based smoke tours (#434/#437): reviewed, no change needed:

This branch touches only backend cascade logic (`sudo()` on internal searches) and a migration -
no view, menu, widget or action changed, so there is no new screen for the per-role crawler tours
to reach or differ on. The existing `TestEnrollmentSyncAsRestrictedUser` (plain `TransactionCase`,
driving the cascades `with_user()` as a secretary/secretary-teacher) is the right level of coverage
for this kind of fix, not a tour.
