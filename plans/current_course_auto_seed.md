# Auto-seed the "Current course" (`current_course_id`) on install

**Status: current, not started.** Design only — no code has been written for this yet.

## Why

`res.company.current_course_id` ("Curso actual") is never auto-seeded: neither `post_init_hook`
nor any migration touches it. The code itself already documents this as a known gap
(`res.company.get_current_course_or_raise()`, `models/settings/company.py:109-121`):

> "nothing guarantees an admin has already set it on a freshly installed instance, or in a
> test DB that never configured one."

This surfaced as two real bugs found 2026-09-09 in `tests/test_absence.py`/`test_absence_tour.py`
while reproducing CI PR #426's failure on a genuinely clean install: `date_range()` on an empty
`current_course_id` returns `False`, and code that assumed a course was already configured broke
with `TypeError: 'bool' object is not subscriptable`. Both were worked around locally (the test
classes now create a fallback course themselves, mirroring `test_guard_duty_board.py`'s existing
pattern) — this plan is about fixing the actual gap so future code/tests don't need that
workaround at all.

A sibling mechanism already does exactly this, for a different field:
`ems.course._ems_seed_enrollment_default()` (`models/settings/course.py:46-86`) auto-seeds
`is_enrollment_default`/`res.company.enrollment_course_id` from `post_init_hook` (fresh installs)
and from `migrations/18.0.0.22.0/post-migrate.py` (existing installs). This plan builds the
equivalent for `is_current`/`current_course_id`, in the same shape.

## Design

**New method** `ems.course._ems_seed_current_course()` (next to `_ems_seed_enrollment_default`
in `models/settings/course.py`), `@api.model`, idempotent:

1. If some course already has `is_current=True`: don't touch it (same "never override a
   deliberate move" guard `_ems_seed_enrollment_default` already uses) — only backfill
   `current_course_id` on companies that don't have it yet, pointing at that already-flagged
   course.
2. If none is flagged: search the existing `ems.course` records for the one whose real window
   (`date_range()`: 1 September of `start` to 31 August of `end`) actually contains today's date
   — i.e. the academic year genuinely running right now, not just "whatever `start` happens to
   equal this calendar year." This avoids the edge case of running in July/August, where "this
   calendar year" would still belong to the course that started the previous September.
3. If no existing course covers today (an install with no `data/custom/ems.course.csv` of its
   own, or one whose CSV doesn't reach far enough): create a new one with the real academic year
   for today (`start`/`end` computed from the actual date — not the `start`/`end` fields' own
   form defaults, `datetime.now().year`/`+1`, which only exist for a manual create from the
   Course screen and don't account for the September cutover).
4. Write `companies.current_course_id = course` through the company selector, exactly like
   `_ems_seed_enrollment_default` does for `enrollment_course_id` — `res.company.write()`
   (`models/settings/company.py:158-164`) already calls `_sync_current_course_flag()` on its own
   whenever `current_course_id` is in the written values, so there's no need to also set
   `course.is_current` by hand.

**Call order matters:** `_ems_seed_current_course()` must run *before*
`_ems_seed_enrollment_default()` in `post_init_hook`. The enrollment-default seed's own logic
("the course after the operational one") already reads `is_current` to decide, and today always
finds it empty, falling back to "the earliest course." Seeding the current course first lets
that already-existing fallback chain start hitting its intended branch instead of its own
fallback.

**Call sites** (same pattern as the sibling method):
- `__init__.py::post_init_hook` — one new line, before the existing call to
  `_ems_seed_enrollment_default()`.
- A new `migrations/<next version>/post-migrate.py` (ORM access, so `post-migrate`, not
  `pre-migrate` — see CLAUDE.md's rule on ORM access in migrations) for installations that
  already exist. **Do not bump the manifest version without the developer's go-ahead** (existing
  CLAUDE.md rule) — propose the version and wait for confirmation before creating the folder.

**Tests** (same pattern as `test_course.py`'s "seeding the enrollment default" section, lines
112-145): flags the course containing today; leaves an already-flagged current course alone
(safe to re-run); creates a new course when none covers today; backfills `current_course_id` on
companies missing it even when a course is already flagged; leaves at most one course flagged.

## Left for whoever implements this

- Whether to log a `_logger.warning` when step 3 has to *create* a course — that's the signal
  that this centre's own `data/custom/` data doesn't reach far enough, useful for whoever
  maintains that installation.
- Whether `test_absence.py`/`test_absence_tour.py` (which today create their own 1999-2000
  filler course when none exists) should be simplified once this seed exists — not required,
  but their manual fallback could become unnecessary if the seed always guarantees a sensible
  course. A cleanup decision, not a blocker.
