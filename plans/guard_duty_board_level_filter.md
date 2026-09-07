# Guard duty board: filter by level

**Status: NOT STARTED / design only.** Drafted 2026-09-07 while working on issue #410 (the
empty-range containment-merge fix in `models/attendance/guard_duty_board.py`), on branch
`410-fix-empty-range-in-guard-timetable`. Deliberately **not** implemented on that branch — the
developer asked to park the design for a separate branch later. Written against the codebase as
of that fix; re-read `get_guard_duty_board_lines()` and the containment-merge helper it introduces
before starting, in case either has moved on by the time this is picked up.

## Motivation

Teacher schedules are being loaded in two halves by two different people: the developer is
loading vocational-training ("ciclos") teachers, a colleague is loading ESO + Batxillerat
teachers. Both want to filter the Guard duty board down to their own half while entering/
reviewing data, instead of seeing every level mixed together.

## Requirement, as described by the developer

Add a level selector next to the existing shift selector
(`static/src/xml/backend/guard_duty_board.xml`'s `o_guard_board_shift_select`). Concretely:

- The level filter decides which **classes** are considered for that day/shift — only the
  subjects/groups belonging to the selected level. Those filtered classes are what build the
  table's rows (the hour ranges) — exactly as `get_guard_duty_board_lines()` already does today,
  just working from a smaller set of teaching entries.
- Once the rows exist, each row's guard-duty column is filled with the teachers who "fit" those
  hours — i.e. whose own guard-duty slot for that day overlaps the row's hour range.
- No level selected (or an explicit "All") keeps today's current behaviour unchanged: every
  level's classes and every guard, exactly as now.

## Design sketch

**No new persistent field or model is needed.** The level of a teaching entry is already
reachable through the existing curriculum hierarchy (`models/curriculum/`: Level → Study →
Subject → Content) via `attendance.group_ids.study_id.level_id`.

**"Level of a guard-duty entry" has to be derived, not stored** — a guard-duty
`resource.calendar.attendance` row has no `group_ids` at all by design (see that field's own NOTE
in `working_schedule.py`), so there is nothing on the row itself to filter by. Per the developer's
own criterion: a teacher counts as "belonging" to a level, for a given weekday, if that same
weekday they have at least one *other* teaching entry (`subject_id`/`group_ids`) whose group's
study's level matches the filter. This reuses the same `entries` recordset
`get_guard_duty_board_lines()` already loads via `_get_guard_duty_board_attendance_ids()` — no
extra query needed, just an extra grouping pass over data already in memory.

**Row/guard matching reuses the containment-merge mechanism from #410**, not a second one: build
each row's hour range from the filtered teaching entries, then fold each guard-duty entry into
whichever row's hour range contains it (same "is period A contained in period B" check, same
`HOUR_EPSILON` tolerance already being introduced for the #410 fix). This feature is a second,
natural caller of that helper — a reason to keep it a general, reusable helper rather than
guard-duty-specific, not a reason to build something new.

A guard-duty entry whose hours don't overlap **any** teaching row of the selected level (e.g. a
"ciclos" teacher's guard slot falls in an hour where only ESO has class) would, under this
reading, produce no row of its own and simply not appear under that level's filtered view — see
open question 1 below.

## Second requirement, added 2026-09-07: label the break ("patio") period once a level is selected

Once a level is selected, a row with empty group cells during that level's own break should be
recognisable as "Patio" (recess), not read as a data gap — as opposed to a row that's empty for
some other reason (e.g. the coordination-time rows the #410 follow-up now hides entirely, see
`get_guard_duty_board_lines()`'s own docstring). Deliberately **not** attempted on the #410 branch
itself, because it turned out to need real investigation first — recorded here so it doesn't have
to be re-derived:

- **The break itself is never a real, per-teacher attendance row.** It only exists on **framework**
  calendars (`resource.calendar.is_framework=True`), which
  `_get_guard_duty_board_attendance_ids()` deliberately excludes (they're not any real teacher's
  actual schedule). Checked against this dev DB (2026-09-07): zero `non_teaching.code='BR'` rows
  exist on any active, non-framework calendar — a teacher's own calendar just has one continuous
  teaching block spanning across the break (e.g. `10:00-11:00`), the break lives "inside" it from
  the students' side without showing up as a gap in the teacher's own row. So there is no
  `non_teaching_is_break`-flagged entry anywhere in the `entries` this method already loads —
  detecting "this row is a break" requires a **new** read against framework calendars, keyed by
  level (`resource.calendar.level_id`, same field `hr.employee._get_derived_break_entries` already
  uses for the same purpose — see `models/employees/employee.py`).
- **The break isn't centre-wide — it's different per level**, confirmed against this dev DB's own
  framework data (2026-09-07):

  | Level group | Break periods (Monday, same Tue-Fri) |
  |---|---|
  | ESO / BTX | `10:00-10:25`, `12:25-12:40` |
  | CFGB / CFGM / CFGS / EFPS / PFI (ciclos) | `11:00-11:25`, `18:00-18:20` |

  This is exactly why the developer asked to defer this to the level-filter feature instead of
  attempting a centre-wide approximation on #410: without knowing which level's rows are being
  rendered, there is no single correct "this row = patio" answer — `10:00-10:25` is break for
  ESO/BTX but a normal teaching period for every ciclos group, and vice versa for `11:00-11:25`.
  Once a level is selected, though, this becomes unambiguous: read that level's own framework(s)'
  `BR` periods and mark any row whose hour range falls inside one as `is_break: True` (or similar)
  for the template to render distinctly (e.g. a "Patio" label in the Time block cell, or a light
  tint — match whatever the live board's current "no background colour" convention prefers, see
  that doc's own "No cell colouring" section).
- Not needed under "All levels" (no level selected) — the ambiguity above is exactly why open
  question 1 above (should a level-quiet guard row show under "All") already treats "All" as the
  fallback, unfiltered view; this labelling is level-filter-specific by nature.

## Open questions to settle before implementing

1. **Guard slot with no overlapping class of the selected level** — does it still need its own
   (mostly blank) row under that level's tab, or is it correct that it only shows under "All"?
   Affects whether a guard commitment during a level-quiet hour is ever visible outside "All".
2. **What exactly is a "level" for this filter** — every `ems.level` record individually, or a
   coarser, centre-specific grouping? The developer's own example groups two levels into one
   filter option ("ESO+Bachillerato"), which doesn't map 1:1 onto `ems.level` records as they
   exist today. Needs clarifying whether the filter operates on `ems.level` directly or needs a
   grouping concept of its own.
3. **Non-teaching, non-guard rows** (CT/AC/CM/WIC, the ones with no group at all) — do they need
   the same "derive from this teacher's other classes that day" treatment as guards, or is it
   enough that the #410 containment-merge already folds them into whatever teaching/guard row
   surrounds them, with no separate level logic of their own?

## Touch points (once the above is settled)

- **Backend**: `get_guard_duty_board_lines()` / `get_guard_duty_board_data()`
  ([models/attendance/guard_duty_board.py](../models/attendance/guard_duty_board.py)) gain a level
  parameter; reuse the period-containment helper introduced for #410.
- **Frontend**: `static/src/js/backend/guard_duty_board.js` (a `state.activeLevel` + a levels list
  alongside `shifts`) and `static/src/xml/backend/guard_duty_board.xml` (a new `<select>` next to
  the shift one).
- **PDF report**: `reports/attendance/report_guard_duty_board.xml` — the "Download PDF" button
  already passes `guard_duty_weekday`/`guard_duty_shift` via context (see
  `test_report_guard_duty_board_scopes_to_one_shift_via_context` in
  `tests/test_guard_duty_board.py`); a `guard_duty_level` context key would follow the same
  pattern.
- **Tests**: `tests/test_guard_duty_board.py` (level filtering of `teaching_entries`/
  `guard_entries`, including the derived-teacher-level logic) and
  `static/tests/tours/guard_duty_board_tour.js` (selecting a level, verifying only that level's
  data shows).
- **i18n**: new selector label + level option names need `ca_ES`/`es_ES` `.po` entries.
- No migration needed — no new field, no XML ID renamed.
