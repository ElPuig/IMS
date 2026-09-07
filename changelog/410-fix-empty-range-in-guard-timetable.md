# Fixes

## Guard duty board no longer shows a near-empty "phantom" row when a period is absorbed by a longer one:

`get_guard_duty_board_lines()` (`models/attendance/guard_duty_board.py`) built one table row per
distinct `(hour_from, hour_to)` tuple found across every teacher's `resource.calendar.attendance`
row for that weekday/shift. Whenever a teacher's own personal schedule ended a slot a few minutes
earlier than the surrounding standard period (e.g. a guard duty ending 13:25-14:00 instead of the
usual 13:25-14:25, or a short coordination duty with neither a group nor guard flag), that shorter
period rendered as its own, mostly or entirely empty row right next to the real one instead of
being read as part of it. Fixed by folding any period fully contained within a longer period
starting at the same time (or earlier) into that longer period's row (`_merge_absorbed_periods()`)
- both the live board and its PDF export use the same underlying method, so both are fixed at
once. Purely a display-layer change - no data is modified.

## Guard duty board no longer shows a row with nothing in it at all:

A follow-up to the fix above: once duplicate rows stopped appearing, a few genuinely empty
periods remained visible - a bare time range with no class in any group and no guard on duty
(e.g. the Wednesday coordination-time slots), adding no useful information. Such a period is now
dropped from the board entirely; a period with a guard but no class (the normal shape of most
guard slots) is unaffected.

# Internal changes

## Shared float-hour comparison tolerance moved out of `hr.employee`:

`HOUR_EPSILON` (the 30-second tolerance used to compare two `hour_from`/`hour_to` floats that are
meant to represent the same moment but can differ by a hair's-width remainder depending on how
each was computed) was private to `hr.employee`'s own break-derivation logic. The guard duty board
fix above needs the exact same tolerance for the same kind of comparison, so it now lives as a
shared constant on `ems.schedule_report_mixin` instead of being duplicated.
