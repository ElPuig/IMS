# Changes:

## Group's classroom field relabeled to "Reference classroom":
- `ems.group.space_id` (the group's own classroom, shown on the group form/list) is now
  labeled "Reference classroom" ("Aula de referència"/"Aula de referencia") instead of
  "Classroom", to distinguish it from the per-slot classroom shown on individual schedule
  attendance rows and the working-schedules import wizard, which keep the plain "Classroom"
  label. Field name (`space_id`) and all business logic are unchanged, only the display
  label.

## Group schedule PDF header now shows the reference classroom:
- `ems.report_group_schedule` (the group's weekly schedule PDF export) now shows the
  group's reference classroom right below the tutor line in the header, when set - mirroring
  how the tutor line is already conditionally shown. No change for a group with no reference
  classroom set. Line spacing between the tutor and classroom lines was tightened so the two
  read as one compact header block instead of two loosely spaced lines.
