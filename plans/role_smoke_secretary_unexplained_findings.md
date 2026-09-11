# Secretary role-smoke tour: 4 unexplained crashes (found, not yet root-caused)

**Status: current as of 2026-09-11.** Found via `tests/test_role_smoke_secretary_tour.py`'s
crawler; currently worked around by skipping these 4 actions in
`static/tests/tours/role_smoke_common.js`'s `SKIP_ACTION_XMLIDS`, so the secretary role-smoke
tour stays green instead of always reporting the same 4 findings every run.

## What's wrong

Logged in as a plain `secretary` user, the crawler's generic "open every reachable action/view"
loop reports these 4 failures every time, in this order, always right after a `res.partner`
(Students-adjacent) action has just been processed:

- `ems.action_attendance_template_tree` (`ems.attendance_template`), view=list
- `ems.action_attendance_session_tree` (`ems.attendance_session_header`), view=list
- `ems.action_strike_list` (`ems.strike`), view=form
- `calendar.action_calendar_event` (native Odoo "Meetings"), view=calendar **and** view=form

All four report the exact same generic message: `The following error occurred in onWillStart:
"Odoo Server Error"`, with **zero** corresponding server-side traceback and **zero** failed RPC
call in the Odoo log for any of them - every `get_views`/`web_search_read`/`onchange` call the
server actually receives for these models returns HTTP 200 with real content.

## What's confirmed NOT the cause (ruled out during investigation)

- **Not the crawler's own now-removed per-action `Promise.race` timeout mechanism** - reproduces
  identically with a plain, unraced `await` (that mechanism was tried and reverted for a
  *different*, confirmed reason - see `role_smoke_common.js`'s own comment on it).
- **Not the `ems.action_student_kanban` hang** (a separate, already-tracked finding - see
  `plans/role_smoke_student_kanban_secretary_hang.md`) contaminating downstream actions - these 4
  still occur identically even after that action was added to the skip list and no longer even
  attempted.
- **Not the two genuinely-broken widgets found and fixed the same day**
  (`widget="timepicker"` on a `Date` field in `views/attendance/attendance_template/form.xml`,
  `widget="one2many_list"` in `views/attendance/attendance_session/form.xml` - neither name is a
  real registered Odoo widget). Fixing both (confirmed via `grep` that neither name exists
  anywhere in any installed addon, Python side had no matching `default_get` guard either) did
  **not** change these 4 findings at all - same actions, same message, same total count, even
  though the existing `TestAttendanceTemplateTour`/`TestAttendanceTemplateColorTour`/
  `TestAttendanceSessionTour` regression tours all still pass cleanly after the fix.
- **Not a stale screenshot/contamination artifact of the crawl loop itself** - the crawler
  correctly caught each error independently and kept going all the way to the end of the menu
  (confirmed: the tour's final auto-saved screenshot shows an unrelated, much-later screen -
  "My Time Off" - proving the loop didn't get stuck or corrupted at the point of these 4
  failures, it simply recorded them and moved on as designed).

## Working theory, not yet verified

`calendar.action_calendar_event` is a **native** Odoo action with no EMS view customization at
all (confirmed: `grep -rln "calendar.event" views/` only matches `attendance_session/calendar.xml`,
an unrelated file for a different model), yet it fails too - this rules out "a bad EMS-authored
view arch" as the common cause across all 4, since two of them (strike, calendar.event) have no
obviously broken widget/field at all. The most likely remaining explanation is some form of
**crawler-speed artifact**: this crawler opens actions far faster back-to-back than any real user
session ever would, and whatever the actual shared trigger is (asset bundle contention, OWL
reactivity batching, a shared debounced RPC), a normal human user - and every existing dedicated
tour, which only ever opens one or two actions per test - would never hit it. Supporting evidence:
none of the other 4 roles (teacher, orientation, coexistence, tac) hit this pattern at all, and
none of them reach as many actions as secretary does (70 ACL rows, the largest of any role) -
consistent with "reachable only past some N-actions-per-session threshold" rather than a
genuinely broken screen.

## How to actually investigate this (next steps)

1. Reproduce with `watch=True` on `start_tour(...)` in `tests/test_role_smoke_secretary_tour.py`
   and step through with real browser devtools open (Network + Console) right as the crawler
   reaches these 4 actions - headless server logs alone cannot show a purely client-side error's
   real stack trace or timing relative to other in-flight work.
2. If it turns out to be N-actions-per-session related, try artificially slowing the crawl (a
   small `await new Promise(r => setTimeout(r, 200))` between actions) and see if it makes these
   4 stop reproducing - if so, that both confirms the theory and suggests the real fix (throttle
   the crawler's own pace slightly, rather than skip-listing genuinely-fine screens forever).
3. Once root-caused, remove the corresponding xmlid(s) from `role_smoke_common.js`'s
   `SKIP_ACTION_XMLIDS` one at a time and confirm the secretary role-smoke tour still passes.

Once fixed (or confirmed to be something the crawler should permanently work around for a
documented, legitimate reason), delete this file - `git log` keeps the history.
