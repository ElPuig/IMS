from datetime import date

from odoo.tests import tagged, HttpCase

from .common import create_level_study, force_user_language_to_english


@tagged('post_install', '-at_install')
class TestStudentScheduleTour(HttpCase):

    def test_student_schedule_tab_tour(self):
        force_user_language_to_english(self, self.env.ref('base.user_admin'))

        level, study = create_level_study(self, 'TSST', level={'name': 'Tour Schedule Level'}, study={
            'code': 'TSST001', 'name': 'Tour Schedule Study', 'date': date.today(),
        })
        subject = self.env['ems.subject'].create({
            'code': 'TSST001', 'acronym': 'TSST', 'name': 'Tour Schedule Subject',
            'study_ids': [(6, 0, [study.id])],
        })
        space = self.env['ems.space'].create({
            'code': 'TSST-A', 'name': 'Tour Schedule Space',
            'space_type_id': self.env.ref('ems.space_type_classroom').id,
            'work_location_id': self.env.ref('ems.work_location_main').id,
        })
        group = self.env['ems.group'].create({
            'course': 1, 'acronym': 'TSST', 'level_id': level.id, 'study_id': study.id,
            'space_id': space.id, 'shift': 'morning',
        })
        teacher = self.env['hr.employee'].create({'name': 'Tour Schedule Teacher', 'employee_type': 'teacher'})
        calendar = self.env['resource.calendar'].create({'name': 'Tour Schedule Calendar'})
        teacher.resource_calendar_id = calendar
        calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': subject.id, 'group_ids': [group.id], 'name': 'TSST: TSST',
        }])
        student = self.env['res.partner'].create({
            'name': 'Tour Schedule Student', 'contact_type': 'student', 'main_group_id': group.id,
        })
        self.env['ems.enrollment'].create({
            'student_id': student.id, 'group_id': group.id, 'subject_id': subject.id,
        })

        # To observe this tour in a real browser during development:
        #   self.start_tour("/odoo", "ems_student_schedule_tab", login="admin", watch=True)
        self.start_tour("/odoo", "ems_student_schedule_tab", login="admin")
