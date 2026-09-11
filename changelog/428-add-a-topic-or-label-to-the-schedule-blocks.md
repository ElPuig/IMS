# What's new:

## Optional topic on schedule blocks, to split a subject taught by several teachers:
Some subjects (e.g. FP Basica's MP 3161 "Comunicacio i ciencies socials I") are actually split
into several distinct topics, each taught by a different teacher in a different slot (Castella,
Catala, Angles). A new optional "topic" free-text field on each schedule block, editable only
from the teacher's own Schedule tab, lets those be told apart: wherever teachers were previously
grouped just by subject (the teacher's/group's/student's schedule grid and its "Subject ->
Teacher(s)" summary table, on screen and in the exported PDFs), a subject with a topic now shows
one row/block per topic instead of merging every teacher together under one subject. Also
importable from the schedule XML file via a new, optional `<Topic>` node.

# Internal changes:

## Fixed a stale unit test left behind by the topic key change:
`TestEmsScheduleReportMixin.test_report_color_key_falls_back_to_subject` started failing after
`_report_color_key()` began including `topic` in its returned key, since the test's lightweight
mock fixture never set that attribute. Updated the fixture and added a companion test asserting
the key shape when a topic is actually set. Found and fixed during a full, unscoped `./test.sh`
run kicked off right after this branch's changes finished integrating.
