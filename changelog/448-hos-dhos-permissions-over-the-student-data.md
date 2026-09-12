# Fixes:

## Head of Studies / Deputy Head of Studies / Director could not see or edit a student's own data:
- Reported directly by the developer: logging in as a Head of Studies (not the student's own
  tutor) hid the student's personal-data block entirely, and deleting a family contact raised an
  `AccessError` naming `res.partner.relation`.
- Root cause traced across three independent layers, all fixed together (fixing only one would
  have left the bug reproducing at another step): the view's own `read_only_user`/
  `is_tutor_readonly` checks (`models/contacts/contact.py`) never recognized Head of Studies/
  Deputy Head of Studies/Director (`ems.group_head_of_studies`, which `ems.group_director` also
  implies) - only admin, secretary and the literal group tutor; the `res.partner` record rule for
  this group only granted a tutor-scoped write, never a centre-wide one; and EMS carried no ACL
  rows at all for the family-contact relation models (`res.partner.relation`/`.relation.all`,
  from the OCA `partner_multi_relation` module) for this group, so the inline "delete relation"
  button - not routed through any `sudo()` - hit the raw ACL directly.
- `ems.group_head_of_studies` now also implies `ems.group_student_data_reader` (the same
  technical group already used for the Guidance/Coexistence teams' centre-wide read access) for
  full **read** visibility into every student's enrolment, grades, attendance, authorizations,
  strikes and enrolment records - and gets full **read/write** access to the student's own contact
  record and family contacts specifically, matching what Secretary already has. Grades, attendance
  sessions and strikes stay read-only for this role outside a student they actually tutor,
  unchanged from before.
- Covered by new backend tests (`tests/test_student_data_reader.py`,
  `tests/test_contact_relation_wizard.py`) and a new dedicated browser tour
  (`static/tests/tours/contact_head_of_studies_tour.js`) that reproduces the exact reported click
  path - opening the student, adding a family contact, and deleting it via the inline button.
