from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestDepartmentHeadOptionalTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls.env['hr.employee'].create({'name': 'Department Head Optional Tour Manager'})
        cls.department = cls.env['hr.department'].create({
            'name': 'Department Head Optional Tour Department',
            'manager_id': cls.manager.id,
        })

    def test_department_head_can_be_removed_and_saved(self):
        self.start_tour("/odoo", "ems_department_head_optional", login="admin")
