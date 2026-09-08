# What's new

## New guard teaching types for Break and WC:
Added two new non-teaching types, "Guard (Break)" (GB) and "Guard (WC)" (GWC), so break and WC guard duties can be scheduled and tracked separately from regular guards.

## Changing a group's classroom now propagates to its schedule (issue #405):
Editing a group's main classroom (`ems.group.space_id`) no longer leaves the group's own teaching schedule silently pointing at the old room. `write()` now moves every affected teaching block (`resource.calendar.attendance`, plus its synced `ems.attendance_schedule` line) to the new classroom automatically, without ever aborting the save - any other field changed in the same save (e.g. renaming the group at the same time) is never lost, even when a room collision comes up.
- A block that would collide with an already-active session in the new classroom is left in its old room and flagged as pending (`space_pending_group_sync`), instead of blocking the save.
- The group's form shows a persistent banner ("N teaching block(s) could not move...") whenever it has pending conflicts, with a button opening a new resolution wizard (`ems.group_classroom_change_wizard`).
- The wizard reuses the same conflict-resolution widget already built for the working-schedules import wizard (dual classroom pickers per conflicting pair, grouped by conflict kind) - same "Reassign rooms" / "Left prevails" (archives the colliding session) / "Right prevails" (keeps the pending block in its old room, a deliberate accepted divergence) resolutions already offered there.
- `ems.attendance_schedule.check_overlap()`'s own collision-detection query was extracted into a reusable, non-raising `find_room_conflicts()` method (used by both the constraint itself and this new feature) - no behavior change to the existing constraint.
- Covered by `tests/test_group_classroom_change.py` (TransactionCase) and a new browser tour (`ems_group_classroom_change_wizard`).

## Bulk classroom picker on the conflict-resolution widget's card header:
Each conflict card's sub-group (already able to bulk-apply a resolution type to every row at once) can now also bulk-apply a classroom to every row's left or right side in one pick, instead of picking it row by row - developer feedback after resolving a real 20-row batch by hand. Shared by both the working-schedules import wizard and the new group-classroom-change wizard above, since both use the same widget.

# Fixes

## Room conflict resolution left the teacher's own calendar out of sync (issue #405):
Resolving a room conflict via the new group-classroom-change wizard only updated the "official" schedule record, not the teacher's own editable calendar block it derives from - so the group's Schedule tab (and any later re-sync of that teacher's calendar) kept showing the old, colliding room, silently undoing the resolution. Found on real data (SMX1D/SMX2D) right after building the feature; fixed so both sides always move together, and the 20 real rows already affected on this box were corrected.

# Internal changes

## The teacher's own calendar is now the sole trigger for the official teaching schedule:
Following the room-conflict-resolution bug above, editing a teacher's calendar (create, edit, or delete a teaching block) now automatically keeps `ems.attendance_schedule`/`ems.attendance_template` in sync on its own, via a new automatic hook - nothing outside this mechanism writes those two models directly anymore. Built bottom-up, in small, independently-tested pieces (a pure decision function, per-template appliers, a per-teacher entry point, the automatic hook itself, then unifying every existing caller onto it), each one verified before the next was built on top of it. Along the way, three real design bugs were found and fixed: a group with no classroom could crash the background sync instead of being skipped; an early fix for that accidentally deleted an already-correctly-roomed schedule; and a latent bug (never previously exercised) dropped a co-teacher's own classroom when their template got rebuilt around them. Two shared helper methods (`_relocate_via_calendar_blocks`/`_archive_via_calendar_blocks`) now let any caller resolving a room conflict move or archive a session by touching only the calendar, reused to simplify both the group-classroom-change wizard and the working-schedules import wizard's own conflict resolution (fixing the same "calendar left stale" class of bug there too), and a similar direct-write pattern in `ems.group`'s own automatic (no-collision) classroom-change path.

## One-time backfill for calendar blocks that predate the schedule-link column:
A handful of calendar blocks created before the `attendance_schedule_id` link column existed (or before the automatic sync hook above did) had no link to their corresponding schedule line - migrated by re-running the existing calendar-driven rebuild tool (`regenerate_all_from_calendars`, already used by earlier migrations) once more, closing the gap for every teacher with no unresolved conflicts.

## The course-transition wizard no longer manages the teaching schedule by hand either:
Rounding off the two items above, the end-of-year course transition's own archival step used to work out by hand which schedule records a departing teacher's calendar change implied (a fallback lookup for older data, plus its own logic for whether to drop just that teacher or archive the whole class). It now simply archives the calendar blocks that are moving on and lets the same automatic mechanism keep the official schedule in sync, exactly like every other part of the app already does - one less place doing its own version of the same job, and one less way for the two to quietly drift apart. Three tests that specifically exercised the old drifted-data fallback were removed, since that state can no longer occur; the behavior they protected remains fully covered by the general schedule-sync test suite.

## Two test-only gaps found by the first full unscoped test run of this branch:
A security-group-reference check was flagging two of this branch's own model names as broken security group references, purely from a naming coincidence (`ems.group_classroom_change_wizard` looks like a security group id but isn't one) - tightened to only trust matches that actually look like a group reference. Separately, one browser tour for the working-schedules import wizard's conflict screen built its "already-existing session" fixture directly in the database without a matching calendar entry - a shortcut that stopped being valid once the calendar became the single source of truth (see above), so the tour's own conflict resolution had nothing to move and failed. Fixed the fixture, not the feature - the equivalent non-browser test already used a realistic, calendar-linked setup and was never affected.

# Changes

## "Another Coordinations" teaching type marked as fixed:
The AC non-teaching type is now flagged as fixed, matching how other schedule-fixed types (like Guard) are already treated.

## Clearer "Fixed schedule" column caption:
Simplified the confusing "Always a fixed-schedule commitment" label (and its Catalan/Spanish translations) on the non-teaching type view to just "Fixed schedule" / "Horari fix" / "Horario fijo".
