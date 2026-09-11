# Fixes

## Group/student schedule tab: "Break" row missing or squeezed on some groups:
- `schedule_attendance_ids` (the "Schedule" tab widget on a group's and a student's form,
  `readonly_schedule_grid`) had no explicit `limit=` on its embedded `<list>` view, so Odoo
  silently capped it at 40 sub-records. Any group/student whose combined weekly schedule exceeds
  40 periods (common for a full CFGS course load, e.g. DAM1A/DAW1A) lost full field data for the
  overflow records — and the framework's own "Break"/"Patio" rows were consistently among the
  ones cut, so the break either never rendered or only rendered on the first couple of days.
  Fixed by adding `limit="200"` to match the existing convention already used by the teacher's own
  editable schedule grid (`employee/form.xml`, `employee/user_profile_form.xml`).
- Separately, the new overlap/column-split layout (`layoutOverlappingBlocks`, added with the
  student schedule tab) compared `hour_from`/`hour_to` with no float tolerance, so a break period
  whose framework-stored end time (`11.416667`, entered as a literal) is a hair larger than the
  immediately-following class's computed start time (`11 + 25/60` == `11.416666666666666`) was
  misread as a genuine overlap, splitting the break block into two narrow columns instead of
  showing it full-width. Fixed by applying the same `HOUR_EPSILON` tolerance already used
  server-side (`ems.schedule_report_mixin`) to the JS clustering check.
- Confirmed live in a real browser (DAM1A, DAW1A, GA1A) before/after: all three now show the
  break/patio row full-width across every weekday.
