# Fixes:

## Roll-call blocked when a session overlaps another teacher's absence justification:
- A teacher opening the roll-call app for a session that overlapped an `ems.attendance_justification` created by a different teacher (typically the group tutor) got an `AccessError` dialog ("doesn't have 'read' access to ... ems.attendance_justification") and the session was never created, so attendance could not be taken for that slot at all. Reported from production for MP 3162 (SA2A), Thursday 08:00 - 09:00.
- The cause was a chicken-and-egg between the record rule and the data it depends on. `rule_attendance_justification_teacher_own_read` grants read access to teachers listed in the justification's `session_teacher_ids`, a stored compute over `attendance_session_line_ids`, so a teacher only becomes able to read the justification after their own session line is linked to it. That back-link, written by `EmsAttendanceSessionLine.create()`, went through `EmsAttendanceJustification.write()`, whose override reads `attendance_session_line_ids` before doing anything else. The record rules rejected that read, aborting the transaction before the link that would have granted access was ever written.
- Fixed by running the back-link with `sudo()`, consistent with `get_current_justifications()` which is already sudo. It is system-driven bookkeeping, not a user action, and it is what registers the session's teachers on the justification in the first place.
- Affected every teacher of the session, not only the first one to try: the transaction rolled back, so nothing was ever persisted and the slot stayed permanently blocked. Only academic admins and the student's own tutor could open it. Multi-day absences at the start of the course make it easy to hit.

# Internal changes:

## Attendance justification write() no longer reads its lines on every write:
- `EmsAttendanceJustification.write()` built its old-vs-new session line diff (`old_lines_map`) unconditionally, although only the `start_date`/`end_date` branch consumes it. Since reading `attendance_session_line_ids` enforces the record rules, that put a permission check in front of every unrelated write. Now built only when that branch will actually run.
- Regression test added (`test_other_teacher_can_start_session_overlapping_tutor_justification`): a tutor creates a justification, then a different teacher of the same student's group starts an overlapping session. The test invalidates the ORM cache before starting the session, which is what makes the bug reproducible at all: within a single transaction the justification's lines are still cached from its own `create()`, so no fetch happens and the record rules are never enforced.
- `docs/en/developers/attendance/attendance_justification.md` documents the back-link and why its `sudo()` is load-bearing rather than defensive.

# Related with:
- Closes #432
