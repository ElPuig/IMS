# Technical Reference: `ems.schedule_report_mixin` (`models/shared/schedule_report_mixin.py`)

## Overview

`EmsScheduleReportMixin` (`_name = 'ems.schedule_report_mixin'`) holds the two tiny,
stateless helpers shared by the weekly-schedule PDF reports: a stable color assigned per
distinct schedule item, and a float-hour → `"HH:MM"` formatter. Consumed by
`ems.working_schedule` (employees) and `ems.group_schedule` (contacts) — both build a report
grid where each cell needs a consistent color per subject/non-teaching activity and a
human-readable time label.

The module (not the mixin class itself — this is a plain top-level constant, not a method) also
holds `HOUR_EPSILON` (`1/120`, 30 seconds), moved here 2026-09-07 (issue #410) from being private
to `hr.employee` — two `hour_from`/`hour_to` floats meant to represent the exact same moment can
differ by a hair's-width remainder depending on how each was computed, and both
`hr.employee._get_derived_break_entries` (`models/employees/employee.py`) and
`ems.course._merge_absorbed_periods` (`models/attendance/guard_duty_board.py`, see
[attendance/guard_duty_board.md](../attendance/guard_duty_board.md)) need the same tolerance for
the same kind of comparison — kept in one place instead of two copies of the same magic number.

## Methods

| Method | Purpose |
|--------|---------|
| `REPORT_COLOR_PALETTE` | 12 hex colors. Assigned to schedule items in first-seen order by each consumer's own rendering loop (not by this mixin), so two unrelated items only ever share a color once the palette runs out. |
| `_report_color_key(attendance)` | `('non_teaching', id)` if the slot is a non-teaching activity, else `('subject', subject_id)` — the key consumers use to look up (or assign) that item's color. Pure attribute access on whatever `attendance`-shaped object is passed in (a `resource.calendar.attendance` record in practice, extended with `non_teaching`/`subject_id` by `working_schedule.py`) — doesn't call any Odoo-specific method on it. |
| `_format_report_time(value)` | A float hour (e.g. `9.5`) → `"09:30"`. |

## Fixed in this pass (2026-07-29)

Class renamed `ems_schedule_report_mixin` → `EmsScheduleReportMixin`. No bugs found — both
methods are short, pure, and already correct.

## Tests

`tests/test_shared_mixins.py::TestEmsScheduleReportMixin` (new, 3 tests) — since neither
method touches `self` or the database, both are tested against lightweight
`types.SimpleNamespace` doubles rather than real `resource.calendar.attendance` records.
