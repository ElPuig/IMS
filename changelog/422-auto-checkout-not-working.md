# Fixes:

## Automatic teacher check-out silently failing every night, plus stuck/corrupt attendance data (issue #422):
- Root cause found and fixed: `hr.attendance._get_day_start_and_day()` (native Odoo) never resets microseconds when computing a "day start" instant. A `check_in` stamped with microseconds (any real kiosk/systray punch) and a `check_out` without them (typed by hand, or computed by EMS's own auto-close) landing on the same calendar day produced two distinct day-start instants for the same date, and `hr.attendance._update_overtime()` tried to insert two `hr.attendance.overtime` rows for the same `(employee_id, date)` in one statement — a self-collision (`UniqueViolation`) against that table's own unique index. `employee_autocheckout.py` now overrides `_get_day_start_and_day()` to normalize microseconds, fixing it at the single source every write path (`create()`, `write()`, both the EMS and native crons) goes through.
- The nightly EMS auto-checkout cron processed every open attendance in one shared transaction with a bare `try/except` — the first record to hit the bug above poisoned the whole transaction ("current transaction is aborted"), silently failing every *other* employee's close in that same run too, every night. Each attendance close is now wrapped in its own `cr.savepoint()`, so one bad record can no longer take the rest of the batch down with it.
- A close failure is no longer silent: it now schedules a to-do activity for the Academic Admins on the affected employee, in addition to the server log.
- Migration (`18.0.0.24.0`) repairs the production data this left behind: attendances still stuck open, and attendances only closed days later via a different-day kiosk badge-in (producing nonsensical multi-day `worked_hours`, e.g. 60+ hours in one day) — both are force-closed on the same calendar day they were opened, at the employee's last scheduled working hour that day, or 14:00 local time as a fallback when no schedule is found (falling back further to check-in + 1h for the rare case where even 14:00 is still before check-in). Verified against a real, isolated copy of the production database: 56 of 56 affected attendances fixed, 0 failures.

## Taking attendance could be blocked by an unrelated auto-check-in failure:

Opening a roll-call for the first time that day auto-checks the session's teacher in as a side
effect (`ems.attendance_session_header._auto_checkin_teacher()`), but that check-in's own
`hr.attendance.create()` had no failure isolation at all - unlike the sibling create()-triggered
backup close this same issue already protects. A real production incident: a teacher with a
stale attendance from before this fix was deployed hit exactly the collision this fix resolves
while trying to take a roll-call this morning, and the raw database error blocked the roll-call
itself instead of only the side effect that actually failed. The check-in is now isolated in its
own savepoint, logged, and reported to the Academic Admins as a to-do activity on the teacher - a
failure there can no longer stop the primary action (taking attendance) from succeeding.

## Its own new test class assumed the admin's personal timezone always matched the company's:

`tests/test_employee_autocheckout.py` built its "expected" values through `ems.datetime_utils`
(a *company-wide* timezone, used elsewhere for the auto-checkout cron's own retry window) while
the code under test (`_get_last_working_hour`) correctly resolves the *employee's own* timezone
(`hr.employee._get_tz()`, native Odoo). The two only agreed on a database where an admin's
personal timezone had been manually set to match the company's - never guaranteed, and not true
on a clean install - so 4 of its tests failed by exactly that offset on CI. The tests now build
their expected values the same way the code itself does.

## Auto-checkout: share the close logic between the nightly cron and the check-in-triggered backup:
- The check-in-triggered close (already existed as a `create()` safety net) is now a genuine backup for the nightly cron, not just a best-effort side path: it shares the exact same eligibility check and the same failure-isolation/notification logic as the cron, via two new shared methods, instead of duplicating either. A close failure discovered this way can no longer crash the employee's own check-in attempt with a raw, unhandled error either.
- Measured the performance concern before deciding anything: the per-employee lookup this already runs on every check-in is a sub-millisecond, indexed query regardless of how large the attendance table grows — no changes needed there.
- Known, accepted limitation: in the one specific case where the notify happens nested inside the very check-in attempt that Odoo's own validation then blocks anyway, the admin notification isn't always reliably kept (an Odoo mail/activity-module interaction, not a data-safety issue — the attendance itself is never left in a bad state, and the same stuck record gets picked up by the next cron run or check-in regardless).
