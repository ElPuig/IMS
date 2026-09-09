# Fixes

## Secretary staff could not add family contacts to a student (ems.contact.relation.wizard):

Secretary users saw the "Add contact" button on a student's "Contacts & addresses" tab, but clicking it raised an access error naming only "Academic / Administrator" and "Academic / Teacher" as the allowed groups. `security/ir.model.access.csv` granted `ems.contact.relation.wizard` to `ems.group_academic_admin` and `ems.group_teacher` only, while `ems.group_secretary` was never added - even though both the button's own visibility condition and `action_save()`'s guard (`_get_read_only_user()`) already treat secretary as an authorized role, and every other contacts wizard (student update, portal access, graduation, enrollment proposal, student/applicant import) does grant it. The gap was masked in practice because the one secretary who could use the wizard also holds `ems.group_teacher` as a teacher, so the missing line only ever surfaced for secretary-only accounts.

Added the missing `ems.group_secretary` access line, plus two regression tests covering both the moment the error actually happened (opening the wizard via `action_open_relation_wizard`) and the full save path, driven by a fixture user holding `ems.group_secretary` alone - no teacher or tutor group - so a future removal of that line fails the suite instead of reaching users again.
