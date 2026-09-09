# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests.common import TransactionCase

from .common import create_level_study


class TestGroupClassroomSuggestion(TransactionCase):
    """The last deferred follow-up of issue #405: ems.group.space_id can drift from where the
    group actually meets (a room collision gets resolved by moving the group's real classes
    elsewhere, but nobody updates the group's own space_id to match). suggested_space_id
    (computed) detects this - the group's CURRENT room has zero active teaching hours - and
    suggests the room where the group actually spends the most hours; action_apply_suggested_space
    applies it, relying entirely on write()'s existing _propagate_classroom_change to do the real
    work (provably conflict-free by construction: a suggested room only ever exists because the
    OLD room has zero blocks to move away in the first place - see group.py's own docstring)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level, cls.study = create_level_study(cls, 'TGCS', level={'name': 'Test Level (Group Classroom Suggestion)'}, study={
            'code': 'TGCS001', 'name': 'Test Study (Group Classroom Suggestion)', 'date': date.today(),
        })
        cls.subject = cls.env['ems.subject'].create({
            'code': 'TGCS001', 'acronym': 'TGCS', 'name': 'Test Subject (Group Classroom Suggestion)',
            'study_ids': [(6, 0, [cls.study.id])],
        })
        cls.space_a, cls.space_b, cls.space_c, cls.space_old = cls.env['ems.space'].create([{
            'code': code, 'name': name,
            'space_type_id': cls.env.ref('ems.space_type_classroom').id,
            'work_location_id': cls.env.ref('ems.work_location_main').id,
        } for code, name in (
            ('TGCS-A', 'Test Space A (Group Classroom Suggestion)'),
            ('TGCS-B', 'Test Space B (Group Classroom Suggestion)'),
            ('TGCS-C', 'Test Space C (Group Classroom Suggestion)'),
            ('TGCS-OLD', 'Test Old Space (Group Classroom Suggestion)'),
        )])

    def _group(self, space=None):
        return self.env['ems.group'].create({
            'course': 1, 'acronym': 'A', 'level_id': self.level.id, 'study_id': self.study.id,
            'space_id': space.id if space else False,
        })

    def _block(self, group, space, teacher=None, weekday='0', hour_from=9.0, hour_to=10.0, subject=None, teaching=True):
        """A teaching block ('resource.calendar.attendance'), with its matching, already-synced
        'ems.attendance_schedule' line, linked via 'attendance_schedule_id' - built directly via
        the ORM for test determinism, mirroring TestGroupClassroomChange._create_synced_block.
        Uses a FRESH teacher per call by default so several blocks for the same group never
        collide against ems.attendance_template's own (teacher, subject, group) uniqueness
        constraint - pass one explicitly (with a distinct weekday/hour range) to add a second slot
        for the SAME teacher/group. 'teaching=False' creates a bare non-teaching block instead
        (no subject, no template/schedule at all)."""
        if not teacher:
            # A unique name per call: 'hr.employee.create()' gives every teacher their own
            # 'resource.calendar', whose own 'name' is derived from the employee's - two teachers
            # sharing a name within the same course would collide on that calendar's own unique
            # constraint.
            self._extra_teacher_count = getattr(self, '_extra_teacher_count', 0) + 1
            teacher = self.env['hr.employee'].create({
                'name': 'Test Extra Teacher %d (Group Classroom Suggestion)' % self._extra_teacher_count,
                'employee_type': 'teacher',
            })
        if not teaching:
            return self.env['resource.calendar.attendance'].create({
                'calendar_id': teacher.resource_calendar_id.id, 'name': 'Test Guard Duty (Group Classroom Suggestion)',
                'dayofweek': weekday, 'hour_from': hour_from, 'hour_to': hour_to, 'day_period': 'morning',
                'group_ids': [group.id], 'space_id': space.id,
            })
        subject = subject or self.subject
        template = self.env['ems.attendance_template'].search([
            ('teacher_ids', '=', teacher.id), ('subject_id', '=', subject.id), ('group_ids', '=', group.id),
        ], limit=1) or self.env['ems.attendance_template'].create({
            'teacher_ids': [(6, 0, [teacher.id])], 'study_ids': [(6, 0, [self.study.id])],
            'subject_id': subject.id, 'group_ids': [(6, 0, [group.id])],
            'start_date': date(2020, 1, 1), 'end_date': date(2030, 12, 31),
        })
        schedule = self.env['ems.attendance_schedule'].create({
            'attendance_template_id': template.id, 'weekday': weekday,
            'start_time': hour_from, 'end_time': hour_to, 'space_id': space.id,
        })
        return self.env['resource.calendar.attendance'].create({
            'calendar_id': teacher.resource_calendar_id.id, 'name': "%s: %s" % (teacher.name, subject.name),
            'dayofweek': weekday, 'hour_from': hour_from, 'hour_to': hour_to, 'day_period': 'morning',
            'group_ids': [group.id], 'subject_id': subject.id, 'space_id': space.id,
            'attendance_schedule_id': schedule.id,
        })

    def test_no_suggestion_when_no_active_teaching_blocks(self):
        group = self._group(self.space_old)
        self.assertFalse(group.suggested_space_id)

    def test_no_suggestion_when_current_room_has_any_hours(self):
        group = self._group(self.space_a)
        self._block(group, self.space_a, hour_from=9.0, hour_to=10.0)  # 1h, the current room
        self._block(group, self.space_b, hour_from=9.0, hour_to=14.0)  # 5h, more hours elsewhere
        self.assertFalse(group.suggested_space_id)

    def test_suggests_room_with_most_hours(self):
        group = self._group(self.space_old)
        self._block(group, self.space_a, hour_from=9.0, hour_to=11.0)  # 2h
        self._block(group, self.space_b, hour_from=9.0, hour_to=14.0)  # 5h - the winner
        self._block(group, self.space_c, hour_from=9.0, hour_to=10.0)  # 1h
        self.assertEqual(group.suggested_space_id, self.space_b)

    def test_missing_space_id_counts_as_drift(self):
        group = self._group()  # no space_id at all
        self._block(group, self.space_a, hour_from=9.0, hour_to=11.0)
        self.assertEqual(group.suggested_space_id, self.space_a)

    def test_tie_break_by_name_then_id(self):
        group = self._group(self.space_old)
        # Different weekdays - same subject/group at the same overlapping time in two DIFFERENT
        # rooms would be a genuine room conflict (co-teaching requires the same room), not a
        # valid fixture for "the group meets in two rooms on two different days".
        self._block(group, self.space_b, weekday='0', hour_from=9.0, hour_to=12.0)  # Monday, 3h
        self._block(group, self.space_a, weekday='1', hour_from=9.0, hour_to=12.0)  # Tuesday, 3h - tied, but "A" < "B"
        self.assertEqual(group.suggested_space_id, self.space_a)

    def test_excludes_non_teaching_blocks(self):
        group = self._group(self.space_old)
        self._block(group, self.space_a, hour_from=9.0, hour_to=13.0, teaching=False)
        self.assertFalse(group.suggested_space_id)

    def test_excludes_archived_calendar(self):
        group = self._group(self.space_old)
        block = self._block(group, self.space_a, hour_from=9.0, hour_to=13.0)
        block.calendar_id.active = False
        self.assertFalse(group.suggested_space_id)

    def test_apply_suggestion_updates_space_and_propagates(self):
        group = self._group(self.space_old)
        self._block(group, self.space_b, hour_from=9.0, hour_to=11.0)
        self.assertEqual(group.suggested_space_id, self.space_b)

        group.action_apply_suggested_space()

        self.assertEqual(group.space_id, self.space_b)
        self.assertEqual(group.pending_classroom_conflict_count, 0)
        self.assertFalse(group.suggested_space_id)

    def test_search_filter_classroom_drift(self):
        group_drift = self._group(self.space_old)
        self._block(group_drift, self.space_a, weekday='0', hour_from=9.0, hour_to=11.0)
        group_ok = self._group(self.space_a)
        # Different weekday: an unrelated group taught by a different teacher, same subject, same
        # room, same time WOULD be a genuine double-booking, not a fixture quirk to work around.
        self._block(group_ok, self.space_a, weekday='1', hour_from=9.0, hour_to=11.0)
        scope = (group_drift + group_ok).ids

        drifted = self.env['ems.group'].search([('id', 'in', scope), ('suggested_space_id', '!=', False)])
        self.assertEqual(drifted, group_drift)

        not_drifted = self.env['ems.group'].search([('id', 'in', scope), ('suggested_space_id', '=', False)])
        self.assertEqual(not_drifted, group_ok)
