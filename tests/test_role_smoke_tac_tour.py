# -*- coding: utf-8 -*-

from odoo.tests.common import HttpCase, tagged

from .common import create_role_employee, create_role_user, mock_outgoing_email


@tagged('post_install', '-at_install')
class TestRoleSmokeTacTour(HttpCase):
    """Generic crawler covering every screen reachable by a TAC user - see CLAUDE.md's
    "Per-role smoke tours" (issue #434 follow-up). Deliberate negative control: `tac` DOES
    imply hr.group_hr_user (unlike the other 4 roles in this roster), so this should surface
    materially fewer findings - confirming the crawler isn't simply noisy everywhere."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mock_outgoing_email(cls)
        cls.tac_user = create_role_user(cls, 'tac', 'test_role_smoke_tac', name='Role Smoke TAC')
        cls.tac_employee = create_role_employee(cls, cls.tac_user, name='Role Smoke TAC')

    def test_role_smoke_tac_tour(self):
        self.start_tour("/odoo", "ems_role_smoke_tac", login='test_role_smoke_tac', timeout=180)
