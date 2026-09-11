# -*- coding: utf-8 -*-

from odoo.tests.common import HttpCase, tagged

from .common import create_role_employee, create_role_user, mock_outgoing_email


@tagged('post_install', '-at_install')
class TestRoleSmokeOrientationTour(HttpCase):
    """Generic crawler covering every screen reachable by an orientation/guidance user - see
    CLAUDE.md's "Per-role smoke tours" (issue #434 follow-up). Not a feature test: asserts
    nothing about the data shown, only that no reachable action/view_mode crashes for this
    role. `orientation` has zero direct ir.model.access.csv rows of its own (relies entirely on
    implied groups), making it the most fragile role on paper."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mock_outgoing_email(cls)
        cls.orientation_user = create_role_user(
            cls, 'orientation', 'test_role_smoke_orientation', name='Role Smoke Orientation')
        cls.orientation_employee = create_role_employee(
            cls, cls.orientation_user, name='Role Smoke Orientation')

    def test_role_smoke_orientation_tour(self):
        self.start_tour("/odoo", "ems_role_smoke_orientation", login='test_role_smoke_orientation', timeout=180)
