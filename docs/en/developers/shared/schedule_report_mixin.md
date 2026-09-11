# Technical Reference: `ems.schedule_report_mixin` (`models/shared/schedule_report_mixin.py`)

## Overview

`EmsScheduleReportMixin` (`_name = 'ems.schedule_report_mixin'`) started as two tiny, stateless
PDF-formatting helpers and grew, when the student Schedule tab was added, into the **shared
aggregation-to-report pipeline** for every model exposing its own read-only
`schedule_attendance_ids`: a stable colour assigned per distinct schedule item, a float-hour →
`"HH:MM"` formatter, a break-period derivation helper, and the full `get_schedule_report_lines()`/
`get_subject_teachers_summary()` report-building methods. Consumed by `ems.group`
(`models/contacts/group_schedule.py`) and `res.partner` (student, `models/contacts/student_schedule.py`)
— see [Group schedule](../contacts/group_schedule.md) and
[Student schedule](../contacts/student_schedule.md) for how each one wires its own
`schedule_attendance_ids` compute into this shared pipeline. `resource.calendar`
(`ems.working_schedule`, the teacher's own **editable** Schedule tab) only consumes the
coloring/time helpers — its report-line building is genuinely different (one entry per cell,
never a list) and stays its own method, not this mixin's.

The module (not the mixin class itself — this is a plain top-level constant, not a method) also
holds `HOUR_EPSILON` (`1/120`, 30 seconds), moved here 2026-09-07 (issue #410) from being private
to `hr.employee` — two `hour_from`/`hour_to` floats meant to represent the exact same moment can
differ by a hair's-width remainder depending on how each was computed, and both
`hr.employee._get_derived_break_entries` (`models/employees/employee.py`) and
`ems.course._merge_absorbed_periods` (`models/attendance/guard_duty_board.py`, see
[attendance/guard_duty_board.md](../attendance/guard_duty_board.md)) need the same tolerance for
the same kind of comparison — kept in one place instead of two copies of the same magic number.

## Class attributes

| Attribute | Purpose |
|-----------|---------|
| `WEEKDAYS` | `('0', '1', '2', '3', '4')` — Monday-Friday, as `resource.calendar.attendance.dayofweek`'s own string values. |
| `SHIFT_HOURS` | `{'morning': (8, 15), 'afternoon': (15, 22)}` — the realistic hour window `get_schedule_report_lines()` filters/sizes a report to. Kept in sync by hand with the JS copy in `static/src/js/backend/schedule_grid_readonly_field.js`. |
| `REPORT_COLOR_PALETTE` | 12 hex colors. Assigned to schedule items in first-seen order by each consumer's own rendering loop (not by this mixin), so two unrelated items only ever share a color once the palette runs out. |

## Methods

| Method | Purpose |
|--------|---------|
| `_report_color_key(attendance)` | `('non_teaching', id)` if the slot is a non-teaching activity, else `('subject', subject_id, topic or False)` — the key consumers use to look up (or assign) that item's color, and (in `get_schedule_report_lines()`) to decide whether two entries in the same cell collapse into one block or stay separate. Pure attribute access on a `resource.calendar.attendance` record — doesn't call any other Odoo-specific method. **`topic` is part of the key (issue #428, fixed 2026-09-11)**: two teachers can genuinely share the exact same subject/group/slot while teaching different topics (e.g. FP Basica's MP 3161, split by language) — found live on a real teacher's calendar, where a second, unrelated teacher happened to share the exact same subject+group+hour; without topic in the key, the two silently merged into one block, showing only one of the two teachers (chosen arbitrarily by entry order) even though `get_subject_teachers_summary()` correctly listed both. |
| `_format_report_time(value)` | A float hour (e.g. `9.5`) → `"09:30"`. |
| `_get_level_break_entries(level, shift)` | The break/patio period derived from `level`'s schedule framework (`resource.calendar` with `is_framework=True`, matching `level_id`), filtered to `shift`'s `day_period` and `non_teaching.is_break` rows. Returns an empty recordset (no error) when `level` or `shift` is falsy, or the level has no framework. Both consumers' own `_get_break_entries()` delegate here, passing a different `(level, shift)` pair each (a group's own; a student's **main group's**). |
| `_schedule_report_shift()` | Overridable hook: which `shift` value `get_schedule_report_lines()` filters/windows by. Defaults to a plain `self.shift` read (correct for `ems.group`, a real field there); `res.partner` (student) needs no override either, since its own `shift` field is itself `related="main_group_id.shift"`. |
| `get_schedule_report_lines()` | One row per distinct `(hour_from, hour_to)` present in `self.schedule_attendance_ids`, one cell per weekday, entries within a cell grouped by `_report_color_key` into blocks (co-teaching on the same subject+topic collapses into one block per distinct subject/topic/reason, never one per entry — but a different topic of the same subject at the same slot now stays its own block, see above). Filtered to `_schedule_report_shift()`'s `SHIFT_HOURS` window when resolvable. |
| `get_subject_teachers_summary()` | One row per distinct `(subject_id, topic)` pair in `self.schedule_attendance_ids` (issue #428 - a subject split into several topics, e.g. FP Basica's MP 3161, gets one row per topic instead of merging every teacher under a single subject row), with the sorted, de-duplicated `employee_id.display_name` teaching it. Row label built via `attendance.get_subject_display_label()` (`models/employees/working_schedule.py`). |

Both `get_schedule_report_lines()` and `get_subject_teachers_summary()` are inherited
**unchanged** by every consumer — neither overrides either; only `_schedule_report_shift()`
and `_get_level_break_entries()`'s call site differ per model.

## History

- 2026-07-29: class renamed `ems_schedule_report_mixin` → `EmsScheduleReportMixin`.
- Student Schedule tab (see [Student schedule](../contacts/student_schedule.md)): the mixin
  grew from two pure formatting helpers into the full shared pipeline above, so a second
  consumer (`res.partner`) could reuse `get_schedule_report_lines()`/
  `get_subject_teachers_summary()`/the break-derivation logic verbatim instead of duplicating
  `ems.group`'s own copies — see that doc's "Why a student needed its own search" section for
  what's genuinely different between the two consumers (the search feeding
  `schedule_attendance_ids`) versus what's shared (everything downstream of it).

## Tests

`tests/test_shared_mixins.py::TestEmsScheduleReportMixin` — covers only the two methods that
never touch `self.env`/the database (`_report_color_key`, `_format_report_time`), against
lightweight `types.SimpleNamespace` doubles rather than real `resource.calendar.attendance`
records, since neither needs one. The rest of the mixin (`_get_level_break_entries`,
`_schedule_report_shift`, `get_schedule_report_lines`, `get_subject_teachers_summary`) is
real ORM code with no meaningful pure/isolated form to test standalone — it's covered
indirectly, and more realistically, through each consumer's own suite instead
(`tests/test_group_schedule.py`, `tests/test_student_schedule.py`), the same way testing
`ems.group`'s or `res.partner`'s own compute already has to exercise real records regardless
of which class happens to define the shared logic underneath it.
