# Fixes:

## Schedule tab: editing a period lost every group but the first:
The "Schedule" tab's edit widget (`schedule_grid_field.js`) only ever kept a single group per
card, even though `resource.calendar.attendance.group_ids` is a real Many2many and the server
side (`ems.attendance_template`, `ems.teaching`, `apply_schedule_changes`) already treats it as
a genuine set. A period where one teacher runs an identical session for two groups at once in
the same room (e.g. an optional subject combining two official groups) showed only its first
group when re-opened for editing, and saving it silently dropped every other group the period
actually had. The group picker now carries every selected group through load, edit and save,
shown as removable tags with a search-as-you-type field to add more (a first attempt used a
native multi-select, but the developer found it impractical — no visible selected state, and
picking several required a hidden Ctrl/Shift-click). Reported as issue #439 (Cristian Escobar's
Monday 17-18 subject 1709 session, taught to GA1C and GA1D at once in room 2.17).

# Related with:
- Closes #439
