from odoo.tests.common import TransactionCase


class TestEmployeePresenceWidget(TransactionCase):
    """The presence icon on the Teachers/ASP kanban ('hr.hr_kanban_view_employees').

    hr_holidays swaps that icon's widget to "hr_presence_status_private", whose JS declares
    'current_leave_id' as a field dependency (hr_holidays/static/src/components/
    hr_presence_status/hr_presence_status.js). A widget's field dependencies are added to the
    read specification unconditionally, so the view postprocessor's group-based stripping never
    gets a say: the field is requested even for a user the arch hid it from. 'current_leave_id'
    is groups="hr.group_hr_user", and EMS grants 'ems.group_teacher' read access to hr.employee
    (stock Odoo never shows that model to a non-HR user at all - it shows hr.employee.public),
    so every teacher opening the Teachers screen got an AccessError on read from the moment
    hr_holidays became a dependency.

    The arch is the only backend-visible half of this: what the browser then asks for is
    covered by tests/test_employee_teacher_kanban_tour.py.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kanban_view = cls.env.ref('hr.hr_kanban_view_employees')
        cls.teacher_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Teacher (Presence Widget)',
            'login': 'test_teacher_for_presence_widget',
            'groups_id': [(4, cls.env.ref('ems.group_teacher').id)],
        })
        cls.hr_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test HR Officer (Presence Widget)',
            'login': 'test_hr_officer_for_presence_widget',
            'groups_id': [(4, cls.env.ref('hr.group_hr_user').id)],
        })

    def _kanban_arch(self, user):
        return self.env['hr.employee'].with_user(user).get_view(self.kanban_view.id, 'kanban')['arch']

    def test_teacher_kanban_uses_the_public_presence_widget(self):
        arch = self._kanban_arch(self.teacher_user)
        self.assertNotIn('hr_presence_status_private', arch)
        self.assertIn('hr_presence_status', arch)

    def test_hr_officer_kanban_keeps_the_private_presence_widget(self):
        self.assertIn('hr_presence_status_private', self._kanban_arch(self.hr_user))

    def test_teacher_still_has_no_access_to_the_leave_type(self):
        # The fix restricts the widget, never the field: what a teacher may know about a
        # colleague's absence stays "the fact and the interval, never its type" (see
        # ems.guard.duty.board._get_guard_duty_absence_intervals).
        employee = self.env['hr.employee'].create({
            'name': 'Test Employee (Presence Widget)',
            'employee_type': 'teacher',
        })
        with self.assertRaises(Exception):
            employee.with_user(self.teacher_user).read(['current_leave_id'])
