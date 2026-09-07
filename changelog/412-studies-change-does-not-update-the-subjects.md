# What's new:

## Subject enrollments auto-refresh from the enrollment template when a student's study changes:
- Changing a student's **Studies** field now automatically picks the first group (alphabetically) of the new study as the Main Group, and regenerates the student's `ems.enrollment` (subject enrollment) lines from the enrollment template configured for that study and course - the same subjects a proposal for that study/course would offer.
- If the new study has no group yet, nothing is auto-enrolled until one is created - no error, just no-op.
- Old subject enrollments not part of the new template are removed, except any that already have grades recorded - those are kept as-is and a note listing them is posted to the student's chatter.
- Scoped to interactive changes on real students only - excludes applicants, and excludes system flows (course transition, enrollment placement confirmation) that already resolve their own group/subjects.
- New `sale.order.template._ems_find_for(study, course)` resolves the exact template for an already-known course, reused by the new refresh logic.

# Fixes:

## Secretary could delete but not create manual subject enrollments from the student form:
- `ems.enrollment.default_get()`'s manual-creation guard only ever exempted academic admins, despite its own error message claiming a group's tutor could also enroll from the student's form (never actually true - tutors were never exempted there, and the student form's enrollment lines are in fact read-only for a tutor of that same student).
- The secretary's `ir.model.access.csv` row was also read-only (write/create/unlink all denied) while the matching `security/rules/contacts.xml` record rule already declared unrestricted "full access" for secretary - a record rule can only narrow the model-access ceiling, never widen it, so that rule had no practical effect until the ACL itself was corrected.
- Both are now fixed together: secretary can create/edit/delete `ems.enrollment` rows manually from the student's form, and the error message no longer promises tutor access it never actually granted.
