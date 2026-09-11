# -*- coding: utf-8 -*-

from odoo.tests.common import HttpCase, tagged

from .common import create_role_employee, create_role_user, mock_outgoing_email


@tagged('post_install', '-at_install')
class TestRoleSmokeSecretaryTour(HttpCase):
    """Generic crawler covering every screen reachable by a secretary user - see CLAUDE.md's
    "Per-role smoke tours" (issue #434 follow-up). Not a feature test: asserts nothing about
    the data shown, only that no reachable action/view_mode crashes for this role. `secretary`
    has the heaviest ir.model.access.csv footprint of any EMS role (70 rows)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mock_outgoing_email(cls)
        cls.secretary_user = create_role_user(
            cls, 'secretary', 'test_role_smoke_secretary', name='Role Smoke Secretary')
        # 'asp' (Administrative and Services Personnel), not 'teacher' - secretary doesn't
        # imply ems.group_teacher, unlike the other 4 roles in this roster.
        cls.secretary_employee = create_role_employee(
            cls, cls.secretary_user, employee_type='asp', name='Role Smoke Secretary')

    def test_role_smoke_secretary_tour(self):
        self.start_tour("/odoo", "ems_role_smoke_secretary", login='test_role_smoke_secretary', timeout=180)
