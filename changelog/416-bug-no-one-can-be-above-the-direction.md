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
