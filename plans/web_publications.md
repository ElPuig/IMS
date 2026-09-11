# Publishing EMS documents to the centre's website (Plone)

**Status: current, not started.** Design only — no code has been written for this yet. Agreed
2026-09-10 in conversation; the reconnaissance below (Plone version, REST API availability) was
done live against the real site and is factual, everything under "Design" is a proposal.

## Why

The centre publishes PDFs on its own website by hand — group timetables being the recurring
example, re-uploaded every September and every time a schedule changes mid-year. EMS already
generates exactly those PDFs, so the manual step is pure transcription between two systems the
centre already owns.

The document side is done. `ems.action_report_group_schedule`
(`reports/contacts/report_group_schedule.xml`) renders a group's weekly timetable from
`models/contacts/group_schedule.py`; `ems.action_report_working_schedule`
(`reports/employees/report_working_schedule.xml`) does the same for staff. From code, either is a
single `self.env.ref('ems.action_report_group_schedule')._render_qweb_pdf(group.ids)` away from
being bytes in memory. Only the transport to the website is missing.

## What the website actually runs (verified 2026-09-10, not assumed)

`https://elpuig.xeill.net/` is **Plone 5.2, Classic UI, with `plone.restapi` already installed and
serving**. Evidence, gathered with `curl` from this box:

- `Server: waitress` + `X-Powered-By: Zope` — WSGI. Plone 5.2 is the first release shipping
  waitress by default; 5.1 and earlier ran ZServer. So 5.2 or later on that axis.
- Homepage markup carries `id="visual-portal-wrapper"`, `data-pat-plone-modal`,
  `data-pat-pickadate`, `++plone++production` — Mockup/patternslib, i.e. Plone 5 Classic. Plone 6
  Classic uses Bootstrap 5 with different markup, and Volto would be React. Combined with the
  previous point: 5.2.
- `GET / -H "Accept: application/json"` returns
  `401 {"message": "Missing 'plone.restapi: Use REST API' permission"}` — **not** a 404. The REST
  layer is installed and answering; anonymous simply lacks the permission, which is the correct
  and desirable state.

Consequence: no add-on installation, no buildout change, no restart of the web server is needed
on the Plone side. Only a user and a permission (see Prerequisites).

Incidental observation: the resource-registry stamp in the markup reads `++unique++2020-03-24`,
so the site's bundles have not been recompiled since 2020. Nothing blocking, but it suggests the
installation has been untouched for a while — worth knowing before anyone reinstalls add-ons
there.

## Push, not pull — and why

The cheaper alternative was considered and rejected: expose a public Odoo controller
(`/ems/horari/<token>/<group>.pdf`) and have Plone merely link to it. That needs almost no code
and can never go stale.

It loses on availability. The website must keep serving timetables when Odoo is down, under
maintenance, or simply not reachable from outside the centre's network — which is the normal
state of an internal management system. Pull also puts a heavy QWeb render on the public request
path. Push it is: EMS renders and uploads, Plone serves static files from then on.

## The shape of the integration, and why it looks like LimeSurvey

EMS has no "integration framework", and this plan deliberately does not invent one. It has two
integrations built in two different shapes, each correct for its own case:

- **Google Workspace** (`models/shared/google_workspace_mixin.py` + one
  `google_workspace_integration.py` per model) has **no menu at all**. Creating an account is an
  attribute of a student or an employee, so the buttons live on those records.
- **LimeSurvey** (`models/communications/limesurvey.py`) has its own models and its own *Surveys*
  entry under **Communications**, because a survey campaign is an entity with a life of its own —
  state, recipients, follow-up.

A web publication belongs to the second family. It has state (published or not, at which URL,
when, whether it failed) and it hangs off no existing record: the PDF belongs to the group, but
the *publication* does not — it is a fact with its own history. That is what earns it a screen,
**not** the fact that it happens to be an integration.

**Naming matters here.** The section is "Website" (concrete), never "Integrations" (abstract). An
abstract bucket would invite unrelated future integrations — Esfera, Moodle — to be dumped in it
purely because they are integrations, when each belongs wherever its users already work, exactly
as Google Workspace does today. Keeping the criterion "a publication is a stateful object" is what
stops this menu degenerating into a grab bag.

The one thing all three genuinely share is credentials on `res.company` plus a block in
`views/settings/form.xml`. This plan follows that, and nothing more.

## Design

### `ems.web_publication` — one generic model, not one per document type

Fields: source record (`res_model` / `res_id`), report to render, target path in Plone, resulting
public URL, `state` (`draft` / `published` / `error`), last published date, last error message,
`course_id`.

Generic on purpose. "Publish report X of record Y at path Z" covers group timetables, staff
timetables, the centre calendar and whatever comes next, without a new model each time. Records
are created on demand from the source record's own button, not pre-seeded.

Idempotency is the point of storing the path: republishing a changed timetable must **replace** the
file at the same public URL, never accumulate a second copy — any link already handed out or
indexed keeps working.

### `models/shared/plone_mixin.py` — the transport, kept separate

`_plone_login()` (JWT via `POST /@login`), `_plone_upsert_file()`, `_plone_publish()`,
`_plone_delete()`.

Separate from the model on purpose: `ems.web_publication` decides *what and when*, the mixin knows
*how*. LimeSurvey is the cautionary example — its connector and its business logic grew
intertwined in one file, and the file's own header comment documents how hard that made the
threading work.

REST call sequence per document:

1. `POST /@login` with the service user's credentials, or HTTP Basic — decide during Red.
2. `GET <path>` with `Accept: application/json` — 404 means create, 200 means replace.
3. `POST <folder>` with `{"@type": "File", "id": ..., "title": ..., "file": {"data": "<base64>",
   "encoding": "base64", "filename": "...pdf", "content-type": "application/pdf"}}`, or `PATCH
   <path>` with the same body when it already exists.
4. `POST <path>/@workflow/publish` to make it publicly visible.

`requests` is already a dependency (`models/communications/limesurvey.py` imports it), so nothing
new lands in `external_dependencies`.

### Entry points

- Button "Publish to web" on `ems.group`, creating or updating that group's publication record —
  the entry point is where the user already is.
- The Communications menu entry is the overview: what has been published, when, what failed.
- Batches (~40 groups at once) go through `queue_job`'s `with_delay()`, same as Google Workspace,
  so a mass publish cannot time out.

### Settings

A "Website (Plone) Settings" block in `views/settings/form.xml`, beside the existing LimeSurvey and
Google Workspace blocks: `plone_enabled`, `plone_url`, `plone_user`, `plone_pwd_encrypted` (the
encrypted pattern `limesurvey_pwd` and `google_ws_sa_json_encrypted` already use),
`plone_schedules_path`, and `plone_dry_run`.

**`plone_dry_run` is not optional.** It mirrors `google_ws_dry_run` and is what stops a
development database — this box included, whose data is a restored production dump — from writing
into the real public website. It must default to enabled behaviour on any environment whose
`ems.environment_type` is `'dev'`.

### Menu

`menuitem` under `menu_communications` with `sequence="3"`, behind Notices (1) and Surveys (2).
Groups: `ems.group_academic_admin` and `ems.group_head_of_studies` as a starting point — settle it
in the Spec step's access-control table, not here.

## Prerequisites on the Plone side (not EMS work)

- A **dedicated Plone user**, not the Zope root user: the Zope emergency user does not work with
  `plone.restapi`'s JWT `@login`.
- That user needs the `plone.restapi: Use REST API` permission (currently denied to anonymous,
  which is why the 401 above appears) and Contributor/Editor on the target folder only.
- A folder to publish into, with a stable path, since it ends up in the public URLs.

## Suggested phasing

1. Group timetables only, single-record button, dry-run first. Proves auth, upsert, workflow and
   the URL shape end to end against the real site.
2. Mass publish via `queue_job` from the group list.
3. Staff timetables, reusing the same model and mixin unchanged — if this phase needs changes to
   either, the generic design was wrong and should be revisited before adding a third document
   type.
4. Optional: a cron republishing at the start of the course, and republish-on-change when a
   timetable is edited mid-year. Deliberately last — automatic publishing to a public site is the
   step with the most ways to go wrong, and is worth having manual confidence first.

## Open questions, to settle before Red

- Path and naming convention for the published files, and whether they are versioned per course
  (`/horaris/2026-27/1r-dam.pdf`) or overwritten in place. Affects idempotency and any link the
  centre has already published.
- Whether a group's publication should be deleted from Plone when the group disappears or the
  course rolls over, or left as a historical record.
- Whether families/students should reach these from the EMS portal as well, or only from the
  public website.
- Whether the Plone service user's credentials belong on `res.company` (per-centre, consistent
  with the other two integrations) or in system parameters. Default to `res.company` unless a
  reason appears.
