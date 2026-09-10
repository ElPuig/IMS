from odoo.tests.common import HttpCase, tagged

from .common import mock_outgoing_email


@tagged('post_install', '-at_install')
class TestEmployeeTeacherKanbanTour(HttpCase):
    """A teacher opening "Educational Community > Teachers" must actually get the screen.

    Regression test for the AccessError on 'current_leave_id' every teacher hit once
    hr_holidays became an EMS dependency - see tests/test_employee_presence_widget.py for the
    full explanation of why only a browser can catch this one.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Creating a teacher with no corporate email posts a chatter note
        # (_gw_notify_missing_fields) - see CLAUDE.md's "Email safety in tests".
        mock_outgoing_email(cls)
        # A real teacher session, not admin: admin is an HR officer and would pass every step
        # regardless, which is exactly how this bug reached production unnoticed.
        login = 'test_teacher_kanban_tour'
        cls.teacher_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Teacher Kanban Tour',
            'login': login,
            'password': login,
            'lang': 'en_US',
            'groups_id': [
                (4, cls.env.ref('base.group_user').id),
                (4, cls.env.ref('ems.group_teacher').id),
            ],
        })
        # "0000 " prefix: hr.employee's default _order is "name", so this one sorts first among
        # the pre-existing teachers of this database (same trick as the other employee tours).
        cls.teacher = cls.env['hr.employee'].create({
            'name': '0000 Teacher Kanban Tour',
            'employee_type': 'teacher',
            'private_email': 'teacher.kanban.tour@example.com',
        })

    def test_employee_teacher_kanban_tour(self):
        # To watch this tour in a real browser during development, add watch=True below.
        self.start_tour("/odoo", "ems_employee_teacher_kanban", login='test_teacher_kanban_tour')
