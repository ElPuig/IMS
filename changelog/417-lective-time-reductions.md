# What's new:

## Teaching hour reduction types (age-based reductions, e.g. R55):
- New catalog model `ems.teaching_reduction_type` (code, name, reduction hours), managed from **Educational Community → Configuration → Schedules → Teaching hour reduction types** — same access pattern as `ems.non_teaching_type` (Department Chief manages, Teacher/Secretary read-only).
- Seeded with one record: `R55` / "Reduction for teachers aged 55 and over" / 2 hours.
- Teachers can be assigned several reduction types at once from a new "Teaching hour reductions" section on the employee form's Human Resources tab (`hr.employee.teaching_reduction_ids`, `many2many_tags`).
- Each assigned reduction type now shows up as its own extra row in the "Weekly teaching hours" column of the Schedule tab's summary table (and the working-schedule PDF report), added as positive hours on top of the teacher's real scheduled hours (developer's own call: 16h of real classes + a 2h reduction shows 18h total) — implemented in `resource.calendar.get_schedule_hours_summary()`, reused as-is by both the OWL widget and the PDF report with no template changes needed.
- Covered by a `TransactionCase` suite (`tests/test_teaching_reduction_type.py`) and two tours: a CRUD tour for the catalog (`ems_teaching_reduction_type_crud`) and extended coverage of the employee form tour (`ems_employee_form_tabs`) exercising the new Human Resources section and the schedule breakdown row.
- Full technical docs (`docs/en/developers/employees/teaching_reduction_type.md`, plus updates to `working_schedule.md`) and trilingual admin manual updates (`docs/{en,ca,es}/admin/working-schedules.md`).

# Internal changes:

## Dropped the unused `sequence` field from `ems.non_teaching_type`:
- Removed `sequence` (manual drag-order) from `ems.non_teaching_type` as well as from the new `ems.teaching_reduction_type` (developer feedback: neither list is reordered by anything else in the codebase). Both models now order by `name` instead. Views, seed CSVs, dev docs and i18n references updated accordingly.
