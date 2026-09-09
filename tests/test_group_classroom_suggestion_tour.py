# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import HttpCase, tagged

from .common import create_level_study, force_user_language_to_english


@tagged('post_install', '-at_install')
class TestGroupClassroomSuggestionTour(HttpCase):
    """Last deferred follow-up of issue #405 - browser coverage for the classroom-drift banner
    (form) + "Classroom drift" filter/column (list) on top of the model behaviour already covered
    by tests/test_group_classroom_suggestion.py's TransactionCase tests."""

    def test_group_classroom_suggestion_tour(self):
        force_user_language_to_english(self, self.env.ref('base.user_admin'))
        level, study = create_level_study(self, 'TGCS', level={'name': 'Test Level (Group Classroom Suggestion Tour)'}, study={
            'code': 'TGCST001', 'name': 'Test Study (Group Classroom Suggestion Tour)', 'date': date.today(),
        })
        subject = self.env['ems.subject'].create({
            'code': 'TGCST001', 'acronym': 'TGCST', 'name': 'Test Subject (Group Classroom Suggestion Tour)',
            'study_ids': [(6, 0, [study.id])],
        })
        old_space, suggested_space = self.env['ems.space'].create([{
            'code': code, 'name': name,
            'space_type_id': self.env.ref('ems.space_type_classroom').id,
            'work_location_id': self.env.ref('ems.work_location_main').id,
        } for code, name in (
            ('TGCST-OLD', 'Tour Old Space (Group Classroom Suggestion)'),
            ('TGCST-SUG', 'Tour Suggested Space (Group Classroom Suggestion)'),
        )])
        teacher = self.env['hr.employee'].create({
            'name': 'Tour Teacher (Group Classroom Suggestion)', 'employee_type': 'teacher',
            'work_email': 'tour.teacher.tgcs@example.com',
        })
        control_teacher = self.env['hr.employee'].create({
            'name': 'Tour Control Teacher (Group Classroom Suggestion)', 'employee_type': 'teacher',
            'work_email': 'tour.control.teacher.tgcs@example.com',
        })
        group = self.env['ems.group'].create({
            'course': 1, 'acronym': 'A', 'level_id': level.id, 'study_id': study.id,
            'space_id': old_space.id, 'name': 'Tour Classroom Suggestion Group',
        })
        control_group = self.env['ems.group'].create({
            'course': 2, 'acronym': 'B', 'level_id': level.id, 'study_id': study.id,
            'space_id': old_space.id, 'name': 'Tour Classroom Suggestion Control Group',
        })

        def create_synced_block(teacher_, group_, space, subject_, weekday):
            template = self.env['ems.attendance_template'].create({
                'teacher_ids': [(6, 0, [teacher_.id])], 'study_ids': [(6, 0, [study.id])],
                'subject_id': subject_.id, 'group_ids': [(6, 0, [group_.id])],
                'start_date': date(2020, 1, 1), 'end_date': date(2030, 12, 31),
            })
            schedule = self.env['ems.attendance_schedule'].create({
                'attendance_template_id': template.id, 'weekday': weekday,
                'start_time': 9.0, 'end_time': 10.0, 'space_id': space.id,
            })
            return self.env['resource.calendar.attendance'].create({
                'calendar_id': teacher_.resource_calendar_id.id, 'name': "%s: %s" % (teacher_.name, subject_.name),
                'dayofweek': weekday, 'hour_from': 9.0, 'hour_to': 10.0, 'day_period': 'morning',
                'group_ids': [group_.id], 'subject_id': subject_.id, 'space_id': space.id,
                'attendance_schedule_id': schedule.id,
            })

        # 'group': stays in 'old_space' (its OWN space_id) but its only real teaching happens in
        # 'suggested_space' - a genuine drift the tour resolves by clicking "Apply suggested
        # classroom". 'control_group': the same drift, left untouched throughout the tour, so the
        # "Classroom drift" list filter has exactly one match left by the end. Different weekdays:
        # same room, same time, different teachers/groups would be a genuine double-booking, not a
        # deliberate co-teaching setup.
        create_synced_block(teacher, group, suggested_space, subject, weekday='0')
        create_synced_block(control_teacher, control_group, suggested_space, subject, weekday='1')

        self.start_tour("/odoo", "ems_group_classroom_suggestion", login="admin")
