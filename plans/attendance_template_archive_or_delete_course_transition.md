# Extend archive-or-delete to course_transition_wizard's own template archival

**Status: current as of 2026-09-07, not started.**

## Context

`ems.attendance_template._archive_or_delete()` (added 2026-09-07, see
`docs/en/developers/attendance/attendance_template.md`'s "Archive-or-delete" section) deletes a
superseded/duplicate template outright instead of archiving it forever, but only when none of its
schedule lines (active or archived) ever had a real `attendance_session_ids` entry. Applied so far
to every template-level archival call site in the calendar-sync pipeline (`sync_from_schedule_batch`,
`_archive_stale_schedule_sync`, `regenerate_all_from_calendars`) and to the working-schedule import
wizard's own `db_conflicts` "prevail_left" resolution (`working_schedule.py`).

## What's left

`models/settings/course_transition_wizard.py` has two more template-level `action_archive()` call
sites that were deliberately left untouched in that same pass, to keep its scope to what was
actually asked (repeated working-schedule re-imports leaving clutter):

- The departing-co-teacher correction (`~line 866`): when no remaining teacher still needs a
  template after some teachers leave, it archives the template outright.
- `_templates_to_archive()`'s own end-of-course archival (`~line 1065`): every template belonging
  to a study transitioning to the next course.

Both are the same "fully superseded, nothing left to preserve unless real sessions exist" shape as
the call sites already converted - switching them to `_archive_or_delete()` would very likely be a
small, mechanical change. Not done yet because course transition is explicitly `IRREVERSIBLE` (own
docstring) and has a much larger test surface (`TestCourseTransition`, 127 tests) - worth doing as
its own deliberate pass with the developer's go-ahead, not folded silently into an unrelated fix.

## Next steps if picked up

1. Confirm with the developer whether this scope expansion is wanted.
2. Swap both call sites to `_archive_or_delete()`.
3. Audit `TestCourseTransition` for any assertion on `.active`/existence of a template that would
   now be deleted instead of archived (same pattern already hit in
   `tests/test_working_schedules_import_wizard.py` and `tests/test_attendance_template.py` for the
   sync-pipeline call sites - grep `assertFalse(.*\.active)` / `assertTrue(.*\.active)` scoped to
   template records, not schedule lines).
4. Run `./test.sh TestCourseTransition` (slow - 127 tests, ~20-30s) to confirm.
5. Fold into the same migration (or a follow-up one) that cleans up the existing archived-unused
   backlog, so production doesn't need two separate cleanup passes.
