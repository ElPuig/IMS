# What's new:

## Guard duty board: filter by level (multi-select, e.g. "ESO+Batxillerat" together vs. vocational-training levels):
- Recovered a parked design plan (`plans/guard_duty_board_level_filter.md`, drafted 2026-09-07 alongside issue #410) and resolved its three open questions with the developer before implementing:
  - The filter is a plain multi-select checkbox dropdown over existing `ems.level` records (7 today) — no new grouping model/field, since `ems.group` already has its own `level_id`.
  - A guard-duty entry with no overlapping row of the selected level(s) is hidden under that filter (only visible under "All levels"), not shown almost-empty.
  - Non-teaching, non-guard rows (coordination/meetings) needed no special level logic — confirmed with the developer that the board never surfaces them as their own content in the first place.
- Once a level is selected, `ems.course.get_guard_duty_board_lines()` only builds rows/columns from that level's own teaching entries - that's the only thing the filter controls. A guard shows on any visible row their own duty overlaps, regardless of what level (if any) they otherwise teach: there's no way to know a guard-duty teacher's "own level", and it doesn't matter - being on duty during a visible block is what counts (developer feedback, after a first attempt tried deriving a guard's level from their other classes that day and wrongly hid a real guard-only shift with no teaching entry at all).
- A guard duty scheduled specifically during a level's own break ("Patio"/break, which differs per level group at this centre) now gets its own dedicated row once a level is selected, instead of silently disappearing — read from that level's own schedule framework.
- The "Download PDF" button and report forward the current level selection too, matching the existing weekday/shift scoping.
- New backend tests (level narrowing, guard-belonging derivation, the break/"Patio" row, JSON safety) and a browser tour step exercising the level checkbox filter live in the rendered table.
- User manual (`docs/{en,ca,es}/teachers/guard-duty-schedule.md`) and the technical reference (`docs/en/developers/attendance/guard_duty_board.md`) updated to cover the new filter; new translatable strings ("All levels", the existing "Break" label reused for this new JS usage) have real `ca_ES`/`es_ES` entries, verified against the actual served translation bundle (not just the `.po` diff).

# Fixes:

## Guard duty board level filter: checking every level didn't match "All levels":
- Developer report: with every level checkbox checked, a guard-only shift with no teaching entry that day (e.g. a teacher who only covers guard duty, no class of their own) was silently missing, even though selecting every level should show exactly the same data as selecting none.
- Even after removing the guard-belonging check above, a level-filtered view's rows still only ever come from teaching entries - never from a guard-only period or a "reinforcement" group's period, the way the unfiltered "All levels" view naturally includes both. Fixed by normalizing a selection covering every existing level back to the exact same "All levels" code path, so the two are guaranteed identical rather than coincidentally similar.
