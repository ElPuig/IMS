# What's new

## Grace period before a Google account is deactivated, with a warning email:

Archiving a member of staff or a student no longer suspends their corporate Google Workspace account straight away. The account keeps working for 30 days, and EMS emails the person - to both their personal and their corporate address - stating the exact date it will be suspended, so nobody loses their mailbox or their Drive files without notice. A daily scheduled action does the actual suspension once the date arrives.

Bringing the person back before the deadline (unarchiving them) calls the whole thing off, and the account is never touched at all. Both forms show the pending date in a banner, with a "Cancel scheduled deactivation" button to keep the account while the person stays archived, and the existing "Suspend Google account" button still suspends it immediately for whoever does not want to wait.

## Student accounts are deleted 30 days after being suspended:

Once a student's account has been suspended, it is scheduled for permanent deletion 30 days later, and the student's leaving notice states both dates up front. The student form shows a second banner for the pending deletion, plus a confirm-guarded "Delete Google account" button for doing it without waiting. Reactivating the account (or unarchiving the student) calls the deletion off; if it had already gone through, coming back creates a fresh account with new credentials. Staff accounts are only ever suspended, never deleted.

Deletion only ever applies to departures from now on: students suspended before this feature existed carry no deletion date, and the update deliberately does not give them one, so no existing suspended account is ever deleted without its owner having been warned first. A deleted student's corporate address stays recorded on their file, so it is never handed out to a different student later.

## Finding the accounts with something pending:

The student list (Educational Community > Students) gains two filters, "Google suspension pending" and "Google deletion pending", a group-by on the suspension date, and both dates as optional columns so they can be sorted. The staff list gains the equivalent suspension filter. All of them are restricted to the roles that can actually act on those accounts, matching the buttons on the forms.

## Clearer wording in the student's leaving notice:

The paragraph explaining what happens between the two dates now spells out all three moments explicitly - the account works as usual until the deactivation date, access is gone from that date onwards (included), and the account is deleted on the deletion date - instead of referring back to "the first date". Reworded in the three languages.

# Fixes

## Google account schedule no longer visible to teachers:

The teacher role has unrestricted read access to every contact, so the banners announcing a scheduled suspension or deletion were readable by any teacher opening a former student's file, even though the buttons acting on that account were already restricted to the secretariat and the academic administration. The banners, the new list columns and the new filters now all carry the same restriction as those buttons, with regression tests asserting on the view actually returned per user.

# Internal changes

## Two daily scheduled actions drive the lifecycle:

`ems.ir_cron_gw_staff_lifecycle` and `ems.ir_cron_gw_student_lifecycle` (new `data/main/ir.cron-google_workspace.csv`) run once a day and only enqueue the existing suspension/deletion jobs, so a slow or failing Directory API call never blocks the cron. Both search with `active_test=False`, since every record they look for is archived by definition. The delays live as fixed constants in the shared Google Workspace mixin (`GW_DEACTIVATION_DELAY_DAYS`, `GW_DELETION_DELAY_DAYS`), together with a shared helper that sends a lifecycle warning to every known address of a record.

Hard-deleting a record (`unlink`) keeps suspending the account synchronously as before: there would be no record left to hold the scheduled date, and a hard delete is not the archive path the grace period is about.

## Test coverage for the whole lifecycle:

New `TestEmployeeGoogleWorkspaceLifecycle` and `TestStudentGoogleWorkspaceLifecycle` backend suites cover scheduling, cancelling, both cron stages, deletion and its guards. A new browser tour (`TestStudentGoogleWorkspaceTour`) renders the student form's two banners and their buttons end to end - they are driven by date fields rather than by `google_ws_state`, so no existing state test exercised them - and the staff tour now also covers the banner and its cancel button on an archived teacher. Both tour suites patch the SMTP transport, since archiving now sends a real email.

# Related with

- Closes #388
