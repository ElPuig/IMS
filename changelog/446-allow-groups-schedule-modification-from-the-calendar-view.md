# What's new

## Edit a teaching block's topic and classroom directly from a group's Schedule tab:
- `ems.group_department_chief` and above can now correct a subject's **topic** or
  **classroom** for a specific group directly from the group's own Schedule tab, without
  opening each teacher's form one by one - useful for co-teaching/reinforcement scenarios
  spanning several teachers' calendars.
- An **Edit** button turns each day's blocks into cards, the same familiar layout already used
  to edit a teacher's own schedule - only Topic and Classroom are editable per card; day, hour,
  subject, teacher(s) and groups are shown for reference only and still require the teacher's
  own Schedule tab to change.
- A co-taught block updates every co-teacher's own calendar together, so they never end up
  showing a different classroom for the same class.
- A room collision is never a blocking error: the block is flagged for review and resolved
  through the pre-existing pending-classroom banner and resolution assistant, exactly like
  changing a group's reference classroom or editing a single class from a teacher's own
  calendar already work.
- The group form's pending-classroom banner text was made origin-neutral, since a pending
  block can now come from three different places instead of two.

# Fixes

## Resolving a group's pending classroom conflicts could crash when a co-taught class collided:
- Confirming the classroom-conflict resolution wizard could fail with a database error when
  a co-taught class's room change collided with the same already-active session on both
  co-teachers' sides at once - a scenario the new group-side topic/classroom editing feature
  above makes routine instead of rare. The wizard now skips a conflict line whose underlying
  record already got resolved as a side effect of resolving a related one, instead of
  crashing on it.
