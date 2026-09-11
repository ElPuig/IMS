# -*- coding: utf-8 -*-

from odoo.tests.common import HttpCase, tagged

from .common import create_role_employee, create_role_user, mock_outgoing_email


@tagged('post_install', '-at_install')
class TestRoleSmokeCoexistenceTour(HttpCase):
    """Generic crawler covering every screen reachable by a coexistence user - see CLAUDE.md's
    "Per-role smoke tours" (issue #434 follow-up). Not a feature test: asserts nothing about
    the data shown, only that no reachable action/view_mode crashes for this role."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mock_outgoing_email(cls)
        cls.coexistence_user = create_role_user(
            cls, 'coexistence', 'test_role_smoke_coexistence', name='Role Smoke Coexistence')
        cls.coexistence_employee = create_role_employee(
            cls, cls.coexistence_user, name='Role Smoke Coexistence')

    def test_role_smoke_coexistence_tour(self):
        self.start_tour("/odoo", "ems_role_smoke_coexistence", login='test_role_smoke_coexistence', timeout=180)
