# Students kanban hangs for the secretary role (found via the role-smoke crawler)

**Status: current as of 2026-09-11.** Newly found via
`tests/test_role_smoke_secretary_tour.py`'s crawler, not yet root-caused or fixed. Currently
worked around by skipping the action in `static/tests/tours/role_smoke_common.js`'s
`SKIP_ACTION_XMLIDS` (`ems.action_student_kanban`), so the secretary role-smoke tour stays green
instead of always eating the crawler's full 60s step budget on this one screen.

## What's wrong

Logged in as a plain `secretary` user (no other data beyond the standard `create_role_user`/
`create_role_employee` fixtures), opening the "Students" menu
(`ems.action_student_kanban` - `res.partner`, `view_mode="kanban,list,form"`, context
`{'default_contact_type': 'student', 'search_default_students_only': 1,
'search_default_my_students': 1, 'active_test': False}`) via the crawler's
`actionService.doAction(action, {viewType: 'kanban', clearBreadcrumbs: true})` never resolves
and never rejects - it hangs indefinitely. Confirmed genuine and reproducible (not a fluke, and
not caused by the crawler's own now-removed per-action race/timeout mechanism - see the "the
race we tried and reverted" note in `role_smoke_common.js`): re-run twice with a plain `await`
(no race), both times the whole 60s step timeout fired at exactly this point, with **zero**
downstream contamination of other actions once the race mechanism was removed.

**Key clue: `get_views` for `res.partner` completes fast (145 queries, ~0.13s) and succeeds -
then literally nothing else happens.** No `web_search_read`, no further RPC of any kind, for the
full 60 seconds. This means the hang is client-side, before the view even issues its first data
request - not a slow Postgres query, not a slow controller action, and (per the crawler's own
`action.limit = 1` override, already in effect and not helping here) not simply "too many rows".

## What's confirmed NOT the cause

- **Not the crawler's per-action timeout mechanism** - reproduced with a plain, unraced `await`
  too.
- **Not a genuine AccessError/permission crash** - no server-side traceback or RPC error at any
  point; the request that would carry such an error (`web_search_read`) never even gets sent.
- **Not simply large data volume via the query itself** - `get_views` (which also touches
  `ir.model.access`/loads the arch) completes near-instantly; the stall is strictly *after* that,
  before the first data fetch.

## Working theories, not yet verified

- The kanban view's arch/template is unusually complex (deep XML, many inline widgets) and OWL's
  first-time template compilation for it is what's actually slow - would need to be measured
  directly with browser devtools (a real, non-headless run, or Chrome's own performance profiler
  attached to the headless instance) rather than guessed from server logs alone, since nothing
  server-side can distinguish "compiling a template" from "not yet asked the server for anything".
- `active_test: False` combined with `search_default_my_students: 1` might resolve to a
  domain/onchange computation that itself is expensive to evaluate purely client-side (e.g. a
  facet/filter whose label or count is computed reactively over an already-fetched, unbounded
  recordset) before the actual list request is even built - also unverified.

## How to actually investigate this (next steps)

1. Reproduce with `watch=True` on `start_tour(...)` in `tests/test_role_smoke_secretary_tour.py`
   (per CLAUDE.md's tour-development tip) to see the real browser and use its devtools directly -
   headless server logs alone cannot distinguish a template-compile stall from a hung promise.
2. If it's template compilation: check whether the same kanban is slow for OTHER roles that can
   also reach it (admin can - is it slow there too, just less noticeable because admin's own
   tours never crawl generically?) - if it reproduces for admin too, this is a real,
   user-facing performance bug worth its own issue, independent of role-based access at all.
3. Once root-caused, remove `"ems.action_student_kanban"` from
   `role_smoke_common.js`'s `SKIP_ACTION_XMLIDS` and confirm the secretary role-smoke tour still
   passes on its own.

Once fixed (or confirmed to be something the crawler should permanently skip for a documented,
legitimate reason - e.g. a screen that's inherently unsuitable for a generic no-data-assumptions
crawl), delete this file - `git log` keeps the history.
