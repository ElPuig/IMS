# Fixes

## Emailing an enrollment did not turn an ex-student into an applicant:
- Follow-up to #433, which hung the conversion off `sale.order.action_quotation_sent()`. Odoo never calls that method when the quotation is emailed, which is the path the interface actually takes: `message_post()` marks the order itself with a direct `write({'state': 'sent'})` under the `mark_so_as_sent` context key. `action_quotation_sent()` is only reached from the "Mark as sent" action, the payment flow and EMS's own bulk send button, so a withdrawal or a graduate emailed a new enrollment stayed an ex-student and was still refused portal access.
- `_ems_offer_to_ex_student()` now hangs off the "→ `sent`" branch that `write()` already computes, beside `_ems_unfollow_teachers()`. Every send path ends in that write, including `action_quotation_sent()` itself, so the redundant call there was removed.
- Confirmed against a production dump: the affected enrollment was re-sent almost three minutes after the release that carried the original fix, and the contact was still never converted.
- The bulk send button keeps its own explicit call, which covers re-sending an offer that is already `sent` (no state change, so `write()`'s branch never fires) and is the recovery path for offers sent before the conversion existed.

## Portal access error message no longer describes the wrong step:
- It still said an ex-student comes back only once the new enrollment is confirmed. Sending the enrollment is what turns them into an applicant, and being an applicant is what allows granting portal access; confirmation is the later step that makes them a student again. Reworded in English with matching Catalan and Spanish translations.

# Internal changes

## Tests now drive the real send path instead of the internal method:
- The #433 tests called `action_quotation_sent()` directly, so they passed over a bug that only affected the path the interface uses. Added a case posting with `mark_so_as_sent=True`, which fails against the previous implementation and passes with this one, plus one sending as a secretary rather than as an administrator, since the write on the contact runs with the sender's own access rights.
- The re-send case was reworked: setting the state now converts on its own, so it explicitly rewinds the contact to the state a pre-fix send left behind, which is what the recovery path has to handle.
- `TestEnrollmentPlacement` now neutralizes outgoing email in `setUpClass`, since posting the proposal notifies the order's followers for real, and gives its secretary fixture a sender address of its own.

## Documentation:
- Both developer documents now point at `write()` and spell out why the conversion must not hang off `action_quotation_sent()`, so the trap that produced this bug is recorded rather than left to be rediscovered.
