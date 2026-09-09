# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests.common import TransactionCase

from .common import create_level_study


class TestGroupClassroomChange(TransactionCase):
    """Issue #405: changing ems.group.space_id must propagate to the group's own teaching
    schedule (resource.calendar.attendance + ems.attendance_schedule), never at the cost of
    losing any other field written in the same save - a room collision is left pending
    (space_pending_group_sync) and resolved later via ems.group_classroom_change_wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level, cls.study = create_level_study(cls, 'TGCC', level={'name': 'Test Level (Group Classroom Change)'}, study={
            'code': 'TGCC001', 'name': 'Test Study (Group Classroom Change)', 'date': date.today(),
        })
        cls.subject = cls.env['ems.subject'].create({
            'code': 'TGCC001', 'acronym': 'TGCC', 'name': 'Test Subject (Group Classroom Change)',
            'study_ids': [(6, 0, [cls.study.id])],
        })
        cls.old_space, cls.new_space, cls.other_space = cls.env['ems.space'].create([{
            'code': code, 'name': name,
            'space_type_id': cls.env.ref('ems.space_type_classroom').id,
            'work_location_id': cls.env.ref('ems.work_location_main').id,
        } for code, name in (
            ('TGCC-OLD', 'Test Old Space (Group Classroom Change)'),
            ('TGCC-NEW', 'Test New Space (Group Classroom Change)'),
            ('TGCC-OTH', 'Test Other Space (Group Classroom Change)'),
        )])
        cls.teacher = cls.env['hr.employee'].create({
            'name': 'Test Teacher (Group Classroom Change)', 'employee_type': 'teacher',
            'work_email': 'test.teacher.gcc@example.com',
        })
        cls.other_teacher = cls.env['hr.employee'].create({
            'name': 'Test Other Teacher (Group Classroom Change)', 'employee_type': 'teacher',
            'work_email': 'test.other.teacher.gcc@example.com',
        })
        cls.group = cls.env['ems.group'].create({
            'course': 1, 'acronym': 'A', 'level_id': cls.level.id, 'study_id': cls.study.id,
            'space_id': cls.old_space.id,
        })

    def _create_synced_block(self, teacher, group, space, weekday='0', hour_from=9.0, hour_to=10.0):
        """A teaching block ('resource.calendar.attendance') with its matching, already-synced
        'ems.attendance_schedule' line, linked via 'attendance_schedule_id' - built directly via
        the ORM (rather than through the real sync pipeline) for test determinism."""
        template = self.env['ems.attendance_template'].create({
            'teacher_ids': [(6, 0, [teacher.id])], 'study_ids': [(6, 0, [self.study.id])],
            'subject_id': self.subject.id, 'group_ids': [(6, 0, [group.id])],
            'start_date': date(2020, 1, 1), 'end_date': date(2030, 12, 31),
        })
        schedule = self.env['ems.attendance_schedule'].create({
            'attendance_template_id': template.id, 'weekday': weekday,
            'start_time': hour_from, 'end_time': hour_to, 'space_id': space.id,
        })
        block = self.env['resource.calendar.attendance'].create({
            'calendar_id': teacher.resource_calendar_id.id, 'name': "%s: %s" % (teacher.name, self.subject.name),
            'dayofweek': weekday, 'hour_from': hour_from, 'hour_to': hour_to, 'day_period': 'morning',
            'group_ids': [group.id], 'subject_id': self.subject.id, 'space_id': space.id,
            'attendance_schedule_id': schedule.id,
        })
        return block, schedule

    def test_write_without_affected_blocks_is_noop(self):
        self.group.write({'space_id': self.new_space.id})
        self.assertEqual(self.group.space_id, self.new_space)
        self.assertEqual(self.group.pending_classroom_conflict_count, 0)

    def test_write_moves_block_without_conflict(self):
        block, schedule = self._create_synced_block(self.teacher, self.group, self.old_space)
        self.group.write({'space_id': self.new_space.id})
        self.assertEqual(block.space_id, self.new_space)
        self.assertEqual(schedule.space_id, self.new_space)
        self.assertFalse(block.space_pending_group_sync)
        self.assertEqual(self.group.pending_classroom_conflict_count, 0)

    def test_write_with_conflict_completes_full_write_and_flags_block(self):
        block, schedule = self._create_synced_block(self.teacher, self.group, self.old_space)
        other_group = self.env['ems.group'].create({
            'course': 2, 'acronym': 'B', 'level_id': self.level.id, 'study_id': self.study.id,
            'space_id': self.new_space.id,
        })
        _other_block, other_schedule = self._create_synced_block(self.other_teacher, other_group, self.new_space)

        self.group.write({'space_id': self.new_space.id, 'notes': 'kept me'})

        # The group's own save is never aborted - both the classroom and the unrelated field land.
        self.assertEqual(self.group.space_id, self.new_space)
        self.assertEqual(self.group.notes, 'kept me')
        # The colliding block is left exactly where it was, flagged as pending.
        self.assertEqual(block.space_id, self.old_space)
        self.assertTrue(block.space_pending_group_sync)
        self.assertEqual(self.group.pending_classroom_conflict_count, 1)
        # Nothing touched on the side it collided with.
        self.assertEqual(other_schedule.space_id, self.new_space)
        self.assertTrue(other_schedule.active)

    def _build_conflict_wizard(self):
        block, schedule = self._create_synced_block(self.teacher, self.group, self.old_space)
        other_group = self.env['ems.group'].create({
            'course': 3, 'acronym': 'C', 'level_id': self.level.id, 'study_id': self.study.id,
            'space_id': self.new_space.id,
        })
        other_block, other_schedule = self._create_synced_block(self.other_teacher, other_group, self.new_space)
        self.group.write({'space_id': self.new_space.id})
        self.assertTrue(block.space_pending_group_sync)
        wizard = self.env['ems.group_classroom_change_wizard'].create({'group_id': self.group.id})
        self.assertEqual(len(wizard.conflict_line_ids), 1)
        line = wizard.conflict_line_ids
        self.assertEqual(line.kind, 'plain_conflict')
        self.assertEqual(line.left_attendance_id, block)
        self.assertEqual(line.right_schedule_id, other_schedule)
        return wizard, line, block, schedule, other_schedule, other_block

    def test_wizard_reassign_rooms_resolves_both_sides(self):
        wizard, line, block, schedule, other_schedule, other_block = self._build_conflict_wizard()
        line.write({'resolution': 'reassign_rooms', 'left_space_id': self.new_space.id, 'right_space_id': self.other_space.id})
        wizard.action_confirm()
        self.assertEqual(block.space_id, self.new_space)
        self.assertEqual(schedule.space_id, self.new_space)
        self.assertEqual(other_schedule.space_id, self.other_space)
        # Regression (found 2026-09-08 on real data, SMX1D/SMX2D): the teacher's own calendar block
        # behind the moved-away "existing" session must follow it too, not just the schedule line -
        # otherwise the calendar still shows the old room and a later re-sync silently undoes this.
        self.assertEqual(other_block.space_id, self.other_space)
        self.assertEqual(other_block.attendance_schedule_id, other_schedule)
        self.assertFalse(block.space_pending_group_sync)
        self.assertEqual(self.group.pending_classroom_conflict_count, 0)

    def test_wizard_prevail_right_keeps_block_in_old_room(self):
        wizard, line, block, schedule, other_schedule, other_block = self._build_conflict_wizard()
        line.resolution = 'prevail_right'
        wizard.action_confirm()
        self.assertEqual(block.space_id, self.old_space)
        self.assertEqual(schedule.space_id, self.old_space)
        self.assertEqual(other_schedule.space_id, self.new_space)
        self.assertEqual(other_block.space_id, self.new_space)
        self.assertFalse(block.space_pending_group_sync)

    def test_wizard_prevail_left_archives_existing_session(self):
        wizard, line, block, schedule, other_schedule, other_block = self._build_conflict_wizard()
        line.resolution = 'prevail_left'
        wizard.action_confirm()
        self.assertEqual(block.space_id, self.new_space)
        self.assertEqual(schedule.space_id, self.new_space)
        # The colliding session has no real attendance history behind it - _archive_or_delete()
        # deletes it (and its now-empty template) outright rather than leaving dead clutter behind
        # (see ems.attendance_template._archive_or_delete's own docstring). Its own calendar block
        # is archived, not deleted (resource.calendar.attendance has no such cascade-delete rule).
        self.assertFalse(other_schedule.exists())
        self.assertFalse(other_block.active)
        self.assertFalse(block.space_pending_group_sync)
