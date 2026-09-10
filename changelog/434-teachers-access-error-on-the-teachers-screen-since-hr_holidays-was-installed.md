# Fixes

## Teachers screen unreachable for teachers since hr_holidays was installed:

Any user without `hr.group_hr_user` (i.e. the whole teaching staff) got "You do not have the
necessary permissions to access the fields current_leave_id in Employee (hr.employee)" instead of
the screen when opening Educational Community > Teachers or > ASP.

Root cause: hr_holidays swaps the presence icon on `hr.hr_kanban_view_employees` to its own
`hr_presence_status_private` widget, and that widget's JavaScript declares `current_leave_id`
(declared `groups="hr.group_hr_user"` on `hr.employee`) as a field dependency. Field dependencies
go straight into the read specification the client sends, and are never filtered by the
group-based node stripping the view postprocessor applies to the arch, so the field was requested
even for users the view correctly hid it from. Stock Odoo never shows `hr.employee` to a non-HR
user at all (they get `hr.employee.public`); EMS's own Teachers/ASP screens do, and
`security/ir.model.access.csv` grants `ems.group_teacher` read on the model. The screens broke the
moment hr_holidays became an EMS dependency.

`views/community/employee/kanban.xml` now keeps the private widget for `hr.group_hr_user` and
renders hr's plain `hr_presence_status` (same icon, no leave type, no extra field read) for
everyone else, through a negated group (`groups="!hr.group_hr_user"`). The inherited view carries
`priority=20` so it applies after hr_holidays' own inherit of the same view (priority 16), whose
widget swap it depends on being already in place.

Deliberately not fixed by widening `current_leave_id`'s own groups: what a teacher may know about
a colleague's absence is the fact and the interval, never its type, which is the same line
`ems.guard.duty.board._get_guard_duty_absence_intervals` already draws.

## Regression coverage for what a widget adds to the read specification:

`tests/test_employee_presence_widget.py` asserts the postprocessed kanban arch per group and that
a teacher still cannot read `current_leave_id`. `tests/test_employee_teacher_kanban_tour.py` plus
`static/tests/tours/employee_teacher_kanban_tour.js` open the Teachers kanban, list and form as a
real teacher session: the backend half cannot see this class of bug at all, and the existing
employee tours all log in as users who imply `hr.group_hr_user`, which is why it reached
production unnoticed.

# Internal changes

## Documented the hr_holidays widget/field-dependency interaction:

`docs/en/developers/employees/absence.md` gains a section on why a `groups=`-restricted field can
still reach the client through a widget's `fieldDependencies`, next to the other hr_holidays
interaction already documented there, cross-linked from `employee.md`'s view table.
