# Fixes:

## Department Chief can now be removed without a replacement:
- The Department Chief field on a regular (non-top-level) department's form was marked required as
  soon as the department wasn't sharing its Manager with a parent, which made it impossible to save
  a department after removing its Chief - a legitimate situation mid course-transition, when the
  outgoing Chief is removed before a replacement is assigned. The underlying model already tolerated
  an empty Department Chief (`hr.department._effective_manager()` already returns nothing "left for
  an admin to configure" in that case) - only the form ever blocked it.
- `required` removed from `views/community/department/form.xml`'s Department Chief field
  (`manager_id`). The top-level department's own Area Manager field (the same underlying field,
  relabelled further down the same form) stays required - this change only affects the regular,
  non-top-level Department Chief.
- Added a browser tour (`ems_department_head_optional`) covering the save with no Department Chief,
  since this is a form-level (required attribute) behavior that no backend test can catch.
- Updated the developer reference (`docs/en/developers/employees/department.md`) and the admin
  manual (`docs/{en,es,ca}/admin/teacher-roles.md`) to reflect that Department Chief is optional.

## Only real staff can head a department:
- The technical `hr.employee` backing the superuser account (no real teacher/PAS employee type)
  was selectable, and had actually been picked, as a Department Chief/Seminar Chief/Area Manager -
  it isn't a real member of staff.
- `manager_id`/`seminar_chief_id` now carry a domain restricting the dropdown to teachers and
  administrative/services staff, plus a matching `@api.constrains` so a direct write/import/RPC
  call can't bypass it either. Translated to Catalan and Spanish.

## Nobody can rank above the Director:
- A real Director who was simply a regular (non-heading) member of a department ended up with that
  department's own Chief as their "Manager" - the exact same underlying data bug as the item above
  exposed this: the Director's own Manager was the superuser's technical account. Nothing should
  ever outrank the Director, regardless of which department they nominally belong to.
- `hr.employee._compute_parent_id()` now clears the Director's own Manager unconditionally, before
  any department-cascade rule is even considered; `res.company.write()` now also force-recomputes
  this for the (old|new) Director when `director_id` changes, since that recompute doesn't
  otherwise depend on the company's own field.
- Existing bad data in this environment (a department manager pointing at the technical account)
  cleared as part of verifying the fix.
