# What's new

## Sending an enrollment to a returning ex-student turns them back into an applicant:
- `sale.order.action_quotation_sent()` now calls the new `_ems_offer_to_ex_student()`, which converts the partner of an EMS enrollment being sent from `alumni`/`withdrawal` into `applicant`, unarchives them, points `study_id`/`level_id` at the study on the order (the exit had cleared both) and wipes the `exit_*` metadata. `has_graduated` is left untouched, being a permanent mark.
- `expelled` is deliberately never converted, matching `_ems_admit_student()`, which only readmits `applicant`/`alumni`/`withdrawal`.
- `action_send_enrollment_proposal()` calls the helper on every order it sends, not only the drafts, so re-sending an offer that is already in the `sent` state converts too. The helper is idempotent, so an applicant is skipped.
- Hooked on the send rather than on `create()`: a draft can still be deleted, while sending the offer to the family is a deliberate act.
- `applicant` is not a workaround here, it is the state that already models "holding an offer for a study, with a portal user of their own". `ems.course_transition_wizard._apply_pending_graduates()` already did exactly this for a graduate whose offer nobody had confirmed yet; this brings the manual secretariat path in line with it.

# Fixes

## Returning ex-students could never be granted portal access (circular dependency):
- Portal access requires `contact_type` to be `student`/`applicant`; becoming a `student` requires a confirmed enrollment; `action_confirm()` requires every required authorization to be answered; and those authorizations are answered from the portal. An ex-student coming back was locked out of all four, with no escape hatch: EMS unbinds Odoo's own "Grant portal access" (`views/community/contact/native_action_bindings.xml`) and `contact_type` is `invisible="True"` on the contact form, so the secretariat could not set it by hand either.
- The only workaround was the paper circuit (download the authorization template, have the family sign it, attach the signed PDF and set the status manually), which defeats the purpose of sending the enrollment in the first place.
- Fixed by the applicant conversion above: sending the offer is the one deliberate act outside the loop, and it is what breaks it.

## "Portal access (students/families)" crashed with a NameError instead of showing its error:
- `ems.action_portal_access_bulk` kept its logic inline in the `code` field of the `ir.actions.server`. Odoo's server-action `safe_eval` context provides `env`, `model`, `record`, `records`, `UserError`, `log` and `_logger`, but no `_`, so the guard's `_("...")` raised `NameError: name '_' is not defined` and the RPC surfaced that traceback instead of the intended message. Reported by the secretariat on 2026-09-10.
- The logic moved to `res.partner.action_portal_access_bulk()` (`models/contacts/contact.py`), leaving the server action as a single call. The guard now raises a real translatable `UserError` that also explains why the selection came up empty.
- It was the only server action in the module with an inline `_()`; the other five were checked and are clean.

## A minor applicant's portal credentials went to the minor instead of to their family:
- `_resolve_recipients()` keyed its first branch on `contact_type == 'applicant'`, handing every applicant their own login whatever their age, justified as "at preinscription the family contacts are not known yet". That stops being true for a returning ex-student, whose family relations survive the withdrawal, so a 15-year-old coming back would have been emailed their own credentials, the opposite of what a `student` of the same age gets.
- The branch now tests age first and then the family contacts themselves rather than the contact type: a minor with family contacts on file gets the family, whether student or applicant. A real GEDAC preinscription, which genuinely has none, keeps its previous behaviour and still gets its own login.
- The family lookup moved into a `_family_contacts()` helper, now shared by both branches.

# Internal changes

## Test coverage for the returning-ex-student path:
- `TestEnrollmentPlacement` gains seven cases covering the conversion on send: withdrawal and alumni conversions, `has_graduated` preserved, an expelled student never reinstated, a current student left alone, a plain non-EMS quotation ignored, a re-send of an already-sent offer, and the full circle ending in a confirmed student.
- `TestPortalAccessWizard` gains three cases for recipient resolution (minor applicant with and without family contacts, adult applicant with family contacts) and four for the bulk entry point, including the ex-student selection that used to produce the NameError.
- Blast radius run green: `TestPortalAccessWizard`, `TestEnrollmentPlacement`, `TestEnrollment`, `TestEnrollmentHeader`, `TestExitManagement`, `TestCourseTransition` and `TestPortalActions`, 324 tests in total.

## Documentation and translations:
- `docs/en/developers/contacts/portal_access_wizard.md`: recipient-resolution Mermaid diagram redrawn for the age-first branch, plus a note on how a returning ex-student becomes eligible and why the server action's logic lives in Python.
- `docs/en/developers/enrollment/enrollment.md`: new "Offer to an ex-student" section with a diagram of the circular dependency the conversion breaks.
- Tutor manual (`acces-portal.md`) and secretariat enrollment manual (`manual-matriculacio-preinscripcio.md`) updated in all three languages.
- Catalan and Spanish translations added for the new `UserError`, verified by reading them back through `code_translations` rather than trusting the `.po` diff.
