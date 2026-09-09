# Fixes:

## Daily tutor attendance report was failing for every recipient:

The daily attendance digest sent to tutors crashed while rendering, with
`KeyError: 'attendance_status'`, and was never delivered. Confirmed against a production
dump taken on 2026-09-09: the job for 2026-09-08 failed with that error, and no notification
job for this report had ever reached a completed state.

The cause was a field rename that only landed halfway. `ems.attendance_issue_status.attendance_status`
(Selection) became `attendance_status_id` (Many2one) in 18.0.0.22.0; that version updated the
English source of the mail template but not the `ca_ES`/`es_ES` blocks in `i18n/ca_ES.po` and
`i18n/es_ES.po`, which kept pointing at the old field name in both their `msgid` and their
`msgstr`. This is the second time the exact same class of bug hits these templates - the first
was fixed on 2026-07-28 on the student/family templates, with a written "lesson for future field
renames" that did not prevent the recurrence.

Despite the issue title, this was not limited to tutors reading in Catalan or Spanish: it
affected all of them. `hr_employee.lang` is empty for all 129 employees, so the template's
`{{object.tutor_id.lang}}` never resolves and the render falls back to the executing user's
language - and all 688 active users are `ca_ES`. The correct English body was unreachable in
production.

Fixing the `.po` files repairs development only, because `upgrade.sh` runs with
`--i18n-overwrite` and `deploy.sh` does not: in the no-overwrite branch of Odoo's translation
importer, the value already stored in the database comes last in the jsonb merge and therefore
wins, so an already-broken translation survives every deploy. `migrations/18.0.0.24.0/pre-migrate.py`
repairs it, rehearsed against a restored copy of the production database (the exact record that
failed there now renders in all three languages) and verified idempotent.

Folded into `migrations/18.0.0.24.0/` at merge time (2026-09-09): this branch, like #405 before
it, originally targeted `18.0.0.23.6` as the next fix-level version above `v18.0.0.23.5` - but
`v18.0.0.24.0` had since become this branch's own already-established, still-unreleased target
version across several other merges, so a separate `18.0.0.23.6` folder would never run on an
environment already past it. Merged as its own `migrate()` here instead of keeping a stray
version folder.

# Internal changes:

## Automated guard against stale translations in mail templates:

A documented lesson did not stop this bug from happening a second time, so it is now checked
mechanically. `tests/test_mail_template_translations.py` asserts, for every EMS mail template,
that no translated value uses a QWeb expression or `{{ }}` placeholder absent from its English
source, and includes a test proving the check actually bites.

The gap this closes is that nothing warns about a stale `.po` block for a whole translatable
field: matching is done on the `#:` xmlid reference alone and the `msgid` is discarded, so a
forgotten rename produces no import error, no warning and no failing test - only a queued job
failing in a language nobody develops in. An audit of every EMS mail template and QWeb view
confirmed this template was the only record affected.
