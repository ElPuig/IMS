from datetime import date, timedelta

from odoo.tests import HttpCase, tagged

from .common import create_level_study, force_user_language_to_english, mock_outgoing_email


@tagged('post_install', '-at_install')
class TestGuardDutyBoardTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Approving the absence seeded below posts to the chatter and notifies its followers -
        # see CLAUDE.md's 'Email safety in tests'.
        mock_outgoing_email(cls)

    def test_guard_duty_board_tour(self):
        force_user_language_to_english(self, self.env.ref('base.user_admin'))
        # To observe this tour in a real browser during development:
        #   self.start_tour("/odoo", "ems_guard_duty_board", login="admin", watch=True)

        # The board's own client action reads env.company.current_course_id directly (see
        # guard_duty_board.py's get_current_course_data()/get_guard_duty_board_data(), both of
        # which now raise a friendly error instead of crashing when it's unset) - a fresh CI DB
        # has no "current course" configured at all, unlike this box's own dev DB, so this must
        # be set explicitly rather than assumed. Reusing an already-configured one (if any) avoids
        # colliding with it on the unique_course_name constraint (a freshly create()'d course
        # defaults its start/end to this real year too) - same pattern as test_guard_duty_board.py.
        if not self.env.company.current_course_id:
            self.env.company.current_course_id = self.env['ems.course'].create({'start': 1998, 'end': 1999})

        level, study = create_level_study(self, 'TGDBT', level={'name': 'Tour Guard Board Level 1'}, study={
            'code': 'TGDBT001', 'name': 'Test Study (Guard Duty Board Tour)', 'date': date.today(),
        })
        subject = self.env['ems.subject'].create({
            'code': 'TGDBT001', 'acronym': 'TGDBT', 'name': 'Test Subject (Guard Duty Board Tour)',
            'study_ids': [(6, 0, [study.id])],
        })
        space = self.env['ems.space'].create({
            'code': 'TGDBT-A', 'name': 'Tour Guard Board Space',
            'space_type_id': self.env.ref('ems.space_type_classroom').id,
            'work_location_id': self.env.ref('ems.work_location_main').id,
        })
        group = self.env['ems.group'].create({
            'course': 1, 'acronym': 'TGDBT', 'level_id': level.id, 'study_id': study.id,
            'space_id': space.id, 'shift': 'morning',
        })
        teacher = self.env['hr.employee'].create({'name': 'Tour Guard Board Teacher', 'employee_type': 'teacher'})
        # 'employee_id' (matching every real personal calendar - see hr.employee.create()/
        # course_transition_wizard.py) is what '_get_guard_duty_board_attendance_ids' now uses to
        # tell a teacher's own working schedule apart from Odoo's generic default calendar (e.g.
        # "Standard 40 hours/week", 'employee_id' False) - omitting it here made this fixture
        # indistinguishable from that generic calendar on a clean install (found 2026-09-08 via CI).
        calendar = self.env['resource.calendar'].create({'name': 'Tour Guard Board Teacher Calendar', 'employee_id': teacher.id})
        teacher.resource_calendar_id = calendar
        calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': subject.id, 'group_ids': [group.id], 'name': 'TGDBT: TGDBT',
        }])

        guard_teacher = self.env['hr.employee'].create({'name': 'Tour Guard Board Guard', 'employee_type': 'teacher'})
        guard_calendar = self.env['resource.calendar'].create({'name': 'Tour Guard Board Guard Calendar', 'employee_id': guard_teacher.id})
        guard_teacher.resource_calendar_id = guard_calendar
        guard_calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.env.ref('ems.non_teaching_g').id, 'name': 'Guard',
        }])

        # A distinct afternoon-only teacher, so the tour can prove the shift dropdown actually
        # re-fetches (not just keeps showing the morning data it already has).
        afternoon_teacher = self.env['hr.employee'].create({'name': 'Tour Guard Board Afternoon Teacher', 'employee_type': 'teacher'})
        afternoon_calendar = self.env['resource.calendar'].create({'name': 'Tour Guard Board Afternoon Calendar', 'employee_id': afternoon_teacher.id})
        afternoon_teacher.resource_calendar_id = afternoon_calendar
        afternoon_calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 16, 'hour_to': 17, 'day_period': 'afternoon',
            'subject_id': subject.id, 'group_ids': [group.id], 'name': 'TGDBT: TGDBT (afternoon)',
        }])

        # A second level/study/group (issue #390's level filter), so the tour can prove checking
        # a level in the dropdown actually narrows the board down - not just that the dropdown
        # opens. Own subject: 'subject' above is only valid for 'study' (see 'ems.
        # attendance_template._check_subject_valid_for_all_studies'), not 'study2'.
        level2, study2 = create_level_study(self, 'TGDBT2', level={'name': 'Tour Guard Board Level 2'}, study={
            'code': 'TGDBT2001', 'name': 'Test Study 2 (Guard Duty Board Tour)', 'date': date.today(),
        })
        subject2 = self.env['ems.subject'].create({
            'code': 'TGDBT2001', 'acronym': 'TGDBT2', 'name': 'Test Subject 2 (Guard Duty Board Tour)',
            'study_ids': [(6, 0, [study2.id])],
        })
        space2 = self.env['ems.space'].create({
            'code': 'TGDBT2-A', 'name': 'Tour Guard Board Space 2',
            'space_type_id': self.env.ref('ems.space_type_classroom').id,
            'work_location_id': self.env.ref('ems.work_location_main').id,
        })
        group2 = self.env['ems.group'].create({
            'course': 1, 'acronym': 'TGDBT2', 'level_id': level2.id, 'study_id': study2.id,
            'space_id': space2.id, 'shift': 'morning',
        })
        level2_teacher = self.env['hr.employee'].create({'name': 'Tour Guard Board Level 2 Teacher', 'employee_type': 'teacher'})
        level2_calendar = self.env['resource.calendar'].create({'name': 'Tour Guard Board Level 2 Calendar', 'employee_id': level2_teacher.id})
        level2_teacher.resource_calendar_id = level2_calendar
        level2_calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': subject2.id, 'group_ids': [group2.id], 'name': 'TGDBT2: TGDBT2',
        }])

        # An approved whole-day absence for the morning teacher, on the Monday of the week the
        # board opens on - which is the same Monday its own date picker resolves (see mondayOf()
        # in guard_duty_board.js: a weekend belongs to the week it closes, exactly as
        # date.weekday() does here). Whole day explicitly: 'leave_type_justified' does not seed
        # it, and a request that is neither a whole day nor a span of hours is worth zero hours,
        # which hr_holidays itself then refuses to approve.
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        self.env['hr.leave'].create({
            'employee_id': teacher.id,
            'holiday_status_id': self.env.ref('ems.leave_type_justified').id,
            'request_date_from': monday,
            'request_date_to': monday,
            'ems_full_day': True,
            'ems_submitted': True,
            'ems_responsible_declaration': True,
        }).action_approve()

        self.start_tour("/odoo", "ems_guard_duty_board", login="admin")
