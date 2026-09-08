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

# Changes

## "Another Coordinations" teaching type marked as fixed:
The AC non-teaching type is now flagged as fixed, matching how other schedule-fixed types (like Guard) are already treated.

## Clearer "Fixed schedule" column caption:
Simplified the confusing "Always a fixed-schedule commitment" label (and its Catalan/Spanish translations) on the non-teaching type view to just "Fixed schedule" / "Horari fix" / "Horario fijo".
