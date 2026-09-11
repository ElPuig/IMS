# -*- coding: utf-8 -*-

from odoo.tests.common import HttpCase, tagged

from .common import create_role_employee, create_role_user, mock_outgoing_email


@tagged('post_install', '-at_install')
class TestRoleSmokeTeacherTour(HttpCase):
    """Generic crawler covering every screen reachable by a plain teacher - see CLAUDE.md's
    "Per-role smoke tours" (issue #434 follow-up). Not a feature test: asserts nothing about
    the data shown, only that no reachable action/view_mode crashes for this role. `teacher` is
    the actual role from #434 and the spike role this mechanism was first validated against."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Saving a teacher with no corporate email posts a chatter note - see CLAUDE.md's
        # "Email safety in tests".
        mock_outgoing_email(cls)
        cls.teacher_user = create_role_user(cls, 'teacher', 'test_role_smoke_teacher', name='Role Smoke Teacher')
        cls.teacher_employee = create_role_employee(cls, cls.teacher_user, name='Role Smoke Teacher')

    def test_role_smoke_teacher_tour(self):
        # Crawls every action reachable by this role - can take longer than the default 60s.
        self.start_tour("/odoo", "ems_role_smoke_teacher", login='test_role_smoke_teacher', timeout=180)
