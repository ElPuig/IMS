# What's new

## New Guidance (Orientació) role with centre-wide read access to student data:
Adds a new transversal role, `role_orientation` ("Guidance coordinator"), held by a team of teachers rather than a single person, with its own security-group category (Manager / Administrator) alongside the existing Quality, Coexistence and TAC blocks. Holding the role grants read-only access to every student's file centre-wide - grades and evaluation sessions, academic record (year record, subjects and outcomes), daily attendance lines and justifications, the three attendance-issue tables, strikes, enrolments, contacts and authorizations - instead of only the holder's own tutees. Financial data (sale orders, invoices, payments) is deliberately excluded.

## Academic history now available to the whole teaching staff:
A student's academic history (per-course record, its subjects and outcomes) was readable only by that student's tutor, plus admin, secretary and Head of Studies. It is now readable by every teacher centre-wide, from both the student's own "Academic history" tab and the "Academic history" menu, on the grounds that it is necessary information for the whole teaching community. It stays strictly read-only: creating and editing records remains with the admin, and the secretary keeps its own result adjustment.

## Coexistence coordinator gains the same student-data access:
The coexistence coordinator could previously read every strike centre-wide but nothing else, so an incident had to be judged without the attendance and academic context behind it. It now shares the exact same read-only surface as the new Guidance role, through the same shared technical group rather than a duplicated set of rules.

## Secretary tab and authorization badges now correct for both roles:
The student form's Secretary tab (bonifications, exemptions and enrolment authorizations) resolves its data through the enrolment, which in EMS is a sale order. Both roles now read those, so the tab shows its real content instead of an empty list - and, more importantly, the authorization badges on the student's file no longer read "No" on a student whose family actually signed. Invoices and payments remain out of scope.

# Changes

## Coexistence group now implies the Teacher group:
`group_coexistence` now implies `ems.group_teacher`, matching what `group_tac` and the new `group_orientation` already do. The post is always held by a teacher (`role_coexistence` is `employee_type='teacher'`), and it is also a hard requirement rather than a courtesy: the Students screen is served by an `ir.actions.server`, and Odoo requires write access on the action's own model (`res.partner`) to execute a server action at all - without it a coexistence coordinator hit an `AccessError` opening the screen no matter how complete their read permissions were.

## Students screen no longer narrows to own tutees for these roles:
`action_student_group_enrollment` hard-coded a `tutor_id` filter in server-side code for everyone except admin and secretary, so a row-level permission alone would still have rendered an empty list. The new technical group is now recognized there too. The academic-management root menu, the students list and the academic-record menu were likewise opened up, since a permission with no route to its screen is invisible.

## User documentation:
The teacher manuals gain "Consulting a Student's Academic Data" in Catalan, Spanish and English, covering the academic history now open to every teacher and the centre-wide read access of the Guidance and Coexistence roles. The administrator's "Teacher Roles and Permission Levels" manual gains the new Guidance coordinator role in its permission table, with a note on what it grants and on Coexistence now matching it, also in the three languages.

# Fixes

## Shared test fixture picked a course that never matched what the Secretary tab resolves to:

`tests/common.py::create_student_academic_file` (used by both `TestStudentDataReader` and its
tour) fell back to "the first course found" when none is current - which, under `ems.course`'s
own default ordering, is the *latest* one. `res.partner._ems_enrollment_in_force()` falls back to
whichever course is flagged `is_enrollment_default` instead - seeded onto the *earliest* course
when none is current (see `_ems_seed_enrollment_default`). The two never agreed on a clean
install with no current course configured, so the fixture's own enrolment order never matched
what the lookup resolved to, and the Secretary tab rendered empty in the test - passing on a dev
database that already had a current course, and failing on CI. The fixture now mirrors the same
two-tier fallback the production lookup itself uses.

# Internal changes

## Shared technical group instead of duplicated record rules:
The whole read-only surface (record rules, ACL lines and menu visibility) lives on a single category-less `group_student_data_reader`, implied by both `group_orientation` and `group_coexistence`. Adding a third post later is one `implied_ids` line rather than another ~16 duplicated rules. The group carries its own ACL lines rather than leaning on the Teacher group's, so it stands on its own. The strike-reason catalog deliberately gets an ACL line but no record rule, since no group row-filters it in the first place.

## Browser coverage for the screens, not just the records:
Three browser tours drive the feature as a guidance user and as a plain teacher: the students list served by the role-aware server action, the student form's Secretary tab (authorizations and bonifications) and Academic history tab, and the Academic history list reached from its own menu. This is what a backend test cannot check - both defects found while building this feature were screens filtering themselves in server-side action code or in a client-side loader, which record-level tests render nothing to catch.

## Test coverage for the new access surface:
New `TestStudentDataReader` (23 tests) covering the group wiring, the role catalog entry and its group sync, read access and the absence of write/create/unlink across every in-scope model, the exclusion of financial models, real records read across tutor boundaries, the server-action domain and menu reachability for both posts. Row-level reach is asserted by comparing each model's effective rule domain against the one an academic admin gets, rather than against a hardcoded empty domain.
