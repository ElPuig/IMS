# What's new:

## Students list opens filtered to the teacher's own groups:

The Students screen (Educational Community -> Students) now applies a second default facet, "My students", on top of the existing "Students" one. A teacher lands on the students of the groups they actually work with instead of every student in the centre.

A group counts as "yours" when it is on your timetable (ems.teaching) or when you are its tutor (ems.group.tutor_id, exposed as hr.employee.tutorship_ids). Both sources are needed: a tutoring assignment is normally already an ems.teaching row on the group's tutorship subject, but a tutor set by hand on the group form has no such row - 6 groups were in exactly that state when this was written, 2 of them with students.

A student is matched either by main_group_id or by an ems.enrollment row in one of those groups. The second branch is what covers reinforcement groups (nobody's main group is a reinforcement one - its students are attached through ems.enrollment only) and repeaters/desdobles enrolled in a group that is not their main one.

The facet is removable like any other, so a teacher can always widen the list back to the whole centre.

## Users with no groups are not filtered:

Administration, secretariat and anyone else with no teaching and no tutorship keep seeing every student. _search_is_my_student returns an empty domain for them rather than one matching nothing, so the facet is simply inert.

This is why the action stays a plain ir.actions.act_window: its context is a string evaluated client-side and has no ORM access, so it cannot decide per user whether to add search_default_my_students. The accepted trade-off is that those users do see an inert "My students" facet in the search bar; the secretariat manual says so explicitly. Head of studies and Orientation get no exemption either - if they also teach, they open on their own groups and clear the facet when they need the whole cohort.

# Internal changes:

## New hr.employee._get_own_groups() helper:

Single place resolving "the groups this employee works with" (teaching_ids.group_id | tutorship_ids), shared by res.partner's is_my_student compute and its search method so the two cannot drift apart.

## Browser tour for the new default filter:

New ems_student_my_groups tour, logged in as a seeded teacher rather than admin - admin teaches nothing and would only ever exercise the inert branch. It asserts both facets are applied, that a student outside the teacher's groups is filtered out, and that clearing the facet brings them back.

The pre-existing ems_contact_wpi_readonly_for_non_tutorand tour needed a new first step clearing the facet: its whole point is opening a student the logged-in tutor does NOT tutor, which the new default now hides.
